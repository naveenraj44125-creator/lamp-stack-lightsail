#!/usr/bin/env python3
"""
Generic post-deployment steps for AWS Lightsail
This script handles application deployment and service configuration based on config
"""

import sys
import os
import argparse
from lightsail_common import LightsailBase
from config_loader import DeploymentConfig
from dependency_manager import DependencyManager
from os_detector import OSDetector
from app_configurators.configurator_factory import ConfiguratorFactory

class GenericPostDeployer:
    def __init__(self, instance_name=None, region=None, config=None, os_type=None, package_manager=None):
        # Initialize configuration
        if config is None:
            config = DeploymentConfig()
        
        # Use config values if parameters not provided
        if instance_name is None:
            instance_name = config.get_instance_name()
        if region is None:
            region = config.get_aws_region()
            
        self.config = config
        self.client = LightsailBase(instance_name, region)
        
        # Determine which web server is being used from config
        deps_config = self.config.get('dependencies', {})
        apache_enabled = deps_config.get('apache', {}).get('enabled', False)
        nginx_enabled = deps_config.get('nginx', {}).get('enabled', False)
        self.web_server = 'apache' if apache_enabled else ('nginx' if nginx_enabled else 'apache')
        
        # Set OS information on client for configurators to use
        if os_type:
            self.client.os_type = os_type
        if package_manager:
            self.client.os_info = {'package_manager': package_manager, 'user': 'ubuntu' if package_manager == 'apt' else 'ec2-user'}
        
        # Initialize dependency manager with OS information
        from os_detector import OSDetector
        if os_type and package_manager:
            os_info = OSDetector.get_user_info(os_type, self.web_server)
            os_info['package_manager'] = package_manager
            os_info['service_manager'] = 'systemd'  # Most modern systems use systemd
            self.dependency_manager = DependencyManager(self.client, config, os_type, os_info)
        else:
            self.dependency_manager = DependencyManager(self.client, config)
        
        # Load installed dependencies from the system
        self._detect_installed_dependencies()

    def _detect_installed_dependencies(self):
        """Detect which dependencies are currently installed on the system
        
        IMPORTANT: Only adds dependencies that are BOTH:
        1. Enabled in the config file (dependencies.<name>.enabled: true)
        2. Actually installed/running on the system
        
        This prevents issues like Apache configurator running for Nginx-only deployments
        when Apache happens to be pre-installed on the instance.
        """
        enabled_deps = self.dependency_manager.get_enabled_dependencies()
        
        print(f"📋 Config-enabled dependencies: {enabled_deps}")
        
        # Check which services are actually running/installed
        check_script = '''
set -e
echo "Checking installed services..."

# Check for web servers
systemctl is-active --quiet apache2 && echo "apache:installed" || true
systemctl is-active --quiet httpd && echo "apache:installed" || true
systemctl is-active --quiet nginx && echo "nginx:installed" || true

# Check for databases
systemctl is-active --quiet mysql && echo "mysql:installed" || true
systemctl is-active --quiet mariadb && echo "mysql:installed" || true
systemctl is-active --quiet postgresql && echo "postgresql:installed" || true

# Check for other services
systemctl is-active --quiet redis-server && echo "redis:installed" || true
systemctl is-active --quiet redis && echo "redis:installed" || true
systemctl is-active --quiet memcached && echo "memcached:installed" || true
systemctl is-active --quiet docker && echo "docker:installed" || true

# Check for programming languages
which php > /dev/null 2>&1 && echo "php:installed" || true
which python3 > /dev/null 2>&1 && echo "python:installed" || true
which node > /dev/null 2>&1 && echo "nodejs:installed" || true
which git > /dev/null 2>&1 && echo "git:installed" || true

echo "Service check completed"
'''
        
        success, output = self.client.run_command(check_script, timeout=60)
        detected_on_system = []
        if success:
            for line in output.split('\n'):
                if ':installed' in line:
                    dep_name = line.split(':')[0]
                    if dep_name not in detected_on_system:
                        detected_on_system.append(dep_name)
                    # CRITICAL: Only add if BOTH enabled in config AND installed on system
                    if dep_name in enabled_deps and dep_name not in self.dependency_manager.installed_dependencies:
                        self.dependency_manager.installed_dependencies.append(dep_name)
        
        print(f"🔍 Detected on system: {detected_on_system}")
        print(f"✅ Will configure (enabled AND installed): {self.dependency_manager.installed_dependencies}")

    def deploy_application(self, package_file, verify=False, cleanup=False, env_vars=None):
        """Deploy application and configure services"""
        print(f"🚀 Starting generic application deployment")
        print(f"📦 Package File: {package_file}")
        print(f"🔍 Verify: {verify}")
        print(f"🧹 Cleanup: {cleanup}")
        
        app_type = self.config.get('application.type', 'web')
        app_name = self.config.get('application.name', 'Generic Application')
        app_version = self.config.get('application.version', '1.0.0')
        
        print(f"📋 Application: {app_name} v{app_version}")
        print(f"🏷️  Type: {app_type}")
        print(f"🌍 Instance: {self.client.instance_name}")
        print(f"📍 Region: {self.client.region}")
        
        # Check if Docker deployment is enabled
        docker_enabled = self.config.get('dependencies.docker.enabled', False)
        use_docker_deployment = docker_enabled and self.config.get('deployment.use_docker', False)
        
        if use_docker_deployment:
            print("\n🐳 Docker deployment mode enabled")
            print("="*60)
            print("🐳 DEPLOYING WITH DOCKER")
            print("="*60)
            
            # Use Docker configurator for deployment
            docker_configurator = ConfiguratorFactory.get_docker_configurator(self.client, self.config)
            success = docker_configurator.deploy_with_docker(package_file, env_vars)
            
            if not success:
                print("❌ Docker deployment failed")
                return False
            
            # Skip traditional configuration for Docker deployments
            print("\n✅ Docker deployment completed - skipping traditional service configuration")
        else:
            # Traditional deployment
            print("\n📦 Traditional deployment mode")
            # Deploy application files
            print("\n" + "="*60)
            print("📦 DEPLOYING APPLICATION FILES")
            print("="*60)
            success = self._deploy_application_files(package_file)
            if not success:
                print("❌ Failed to deploy application files")
                return False
            
            # Configure application based on type and dependencies
            print("\n" + "="*60)
            print("🔧 CONFIGURING APPLICATION")
            print("="*60)
            success = self._configure_application()
            if not success:
                print("⚠️  Application configuration had some issues")

            print("\n" + "="*60)
            print("🔧 RUNNING CUSTOM SCRIPTS")
            print("="*60)
            if not self._run_pm2_post_setup_script():
                print("❌ PM2 post-setup script failed")
                return False
        
        # Only run traditional configuration steps if not using Docker
        if not use_docker_deployment:
            # Set up application-specific configurations
            print("\n" + "="*60)
            print("⚙️  APPLICATION-SPECIFIC CONFIGURATIONS")
            print("="*60)
            success = self._setup_app_specific_config()
            if not success:
                print("⚠️  Some application-specific configurations failed")
            
            # Restart services
            print("\n" + "="*60)
            print("🔄 RESTARTING SERVICES")
            print("="*60)
            success = self.dependency_manager.restart_services()
            if not success:
                print("⚠️  Some services failed to restart")
        
            # Verify application services are running after restart
            print("\n🔍 Verifying application services after restart...")
            verify_script = '''
echo "Checking application services..."
for service in nodejs-app python-app; do
    if systemctl list-unit-files | grep -q "^${service}.service"; then
        if systemctl is-active --quiet ${service}.service; then
            echo "✅ ${service} service is running"
        else
            echo "⚠️  ${service} service is not running"
            sudo systemctl status ${service}.service --no-pager || true
        fi
    fi
done
'''
            self.client.run_command(verify_script, timeout=30)
        
        # Set environment variables if provided
        if env_vars:
            print("\n🌍 Setting deployment environment variables...")
            self._set_deployment_env_vars(env_vars)
        
        # Verify deployment if requested
        if verify:
            print("\n" + "="*60)
            print("🔍 VERIFYING DEPLOYMENT")
            print("="*60)
            success = self._verify_deployment()
            if not success:
                print("⚠️  Deployment verification had issues")
        
        # Cleanup if requested
        if cleanup:
            print("\n" + "="*60)
            print("🧹 CLEANING UP TEMPORARY FILES")
            print("="*60)
            self._cleanup_deployment()
        
        # Optimize performance
        print("\n" + "="*60)
        print("⚡ OPTIMIZING PERFORMANCE")
        print("="*60)
        self._optimize_performance()
        
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"✅ Application: {app_name} v{app_version}")
        print(f"🌐 Instance: {self.client.instance_name}")
        print(f"📍 Region: {self.client.region}")
        print(f"🏷️  Type: {app_type}")
        return True
    
    def _get_target_directory(self) -> str:
        """Determine target directory based on app type and dependencies"""
        app_type = self.config.get('application.type')
        
        # Fallback: detect app type from dependencies if not specified
        if not app_type:
            if 'nodejs' in self.dependency_manager.installed_dependencies:
                app_type = 'nodejs'
            elif 'python' in self.dependency_manager.installed_dependencies:
                app_type = 'python'
            elif 'docker' in self.dependency_manager.installed_dependencies:
                app_type = 'docker'
            else:
                app_type = 'web'
        
        print(f"📋 Detected app type: {app_type}")
        
        # Map app types to target directories
        APP_TYPE_DIRS = {
            'nodejs': '/opt/nodejs-app',
            'python': '/opt/python-app',
            'docker': '/opt/docker-app',
        }
        
        # Direct mapping for specific app types
        if app_type in APP_TYPE_DIRS:
            return APP_TYPE_DIRS[app_type]
        
        # For generic types, determine based on installed dependencies
        if app_type in ['web', 'api', 'static']:
            # Check for runtime dependencies first
            if 'nodejs' in self.dependency_manager.installed_dependencies:
                return '/opt/nodejs-app'
            elif 'python' in self.dependency_manager.installed_dependencies:
                return '/opt/python-app'
            
            # Check for web servers and use their document root
            if 'apache' in self.dependency_manager.installed_dependencies:
                return self.config.get('dependencies.apache.config.document_root', '/var/www/html')
            elif 'nginx' in self.dependency_manager.installed_dependencies:
                return self.config.get('dependencies.nginx.config.document_root', '/var/www/html')
            
            # Default for web apps
            return '/var/www/html'
        
        # Default fallback
        return '/opt/app'
    
    def _get_file_owner(self, target_dir: str) -> str:
        """Determine appropriate file owner based on target directory and dependencies (OS-agnostic)"""
        # Get OS-specific user information
        os_type = getattr(self.client, 'os_type', 'ubuntu')
        user_info = OSDetector.get_user_info(os_type, self.web_server)
        
        default_user = user_info['default_user']
        web_user = user_info['web_user']
        web_group = user_info['web_group']
        
        # Node.js and Python apps run as default user
        if target_dir in ['/opt/nodejs-app', '/opt/python-app', '/opt/docker-app', '/opt/app']:
            return f'{default_user}:{default_user}'
        
        # Web server directories need web user
        if any(dep in self.dependency_manager.installed_dependencies for dep in ['apache', 'nginx']):
            return f'{web_user}:{web_group}'
        
        # Default to default user
        return f'{default_user}:{default_user}'
    
    def _deploy_application_files(self, package_file) -> bool:
        """Deploy application files to the appropriate location"""
        target_dir = self._get_target_directory()
        print(f"📁 Target directory: {target_dir}")
        
        # Get expected directory from config
        package_files = self.config.get('application.package_files', [])
        expected_dirs = []
        for pf in package_files:
            # Extract directory name from patterns like "example-app/" or "src/"
            # Only add if it looks like a directory (ends with / or contains /)
            if '/' in pf:
                dir_name = pf.rstrip('/').split('/')[0] if pf else None
                if dir_name and dir_name not in expected_dirs:
                    expected_dirs.append(dir_name)
        
        # First, copy the package file to the remote instance
        print(f"📤 Uploading package file {package_file} to remote instance...")
        # Use home directory instead of /tmp to avoid permission issues
        remote_package_path = f"~/{package_file}"
        
        if not self.client.copy_file_to_instance(package_file, remote_package_path):
            print(f"❌ Failed to upload package file to remote instance")
            return False
        
        # Build directory search logic based on config
        # Only look for wrapper directories (like example-*-app), not subdirectories of the app
        dir_checks = ""
        if expected_dirs:
            # Filter out common app subdirectories that shouldn't be treated as wrapper directories
            app_subdirs = ['config', 'src', 'lib', 'routes', 'middleware', 'database', 'public', 'views', 'models', 'controllers', 'utils', 'helpers', 'assets', 'static', 'templates', 'tests', 'test', 'spec', 'node_modules', 'vendor', 'dist', 'build']
            wrapper_dirs = [d for d in expected_dirs if d not in app_subdirs and not d.startswith('.')]
            
            if wrapper_dirs:
                for dir_name in wrapper_dirs:
                    dir_checks += f'''
if [ -d "./{dir_name}" ]; then
    EXTRACTED_DIR="./{dir_name}"
    echo "✅ Found configured wrapper directory: {dir_name}"
elif'''
                dir_checks += ''' [ -z "$EXTRACTED_DIR" ]; then
    EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "example-*-app" | head -n 1)
fi'''
            else:
                # No wrapper directories found in config, look for example-*-app pattern
                dir_checks = '''EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "example-*-app" | head -n 1)'''
        else:
            dir_checks = '''EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "example-*-app" | head -n 1)'''
        
        script = f'''
set -e
echo "Deploying application files to {target_dir}..."

# Create backup of existing files
if [ -d "{target_dir}" ] && [ "$(ls -A {target_dir})" ]; then
    BACKUP_DIR="/var/backups/app/$(date +%Y%m%d_%H%M%S)"
    sudo mkdir -p "$BACKUP_DIR"
    sudo cp -r {target_dir}/* "$BACKUP_DIR/" || true
    echo "✅ Backup created at $BACKUP_DIR"
fi

# Extract application package from home directory
echo "Extracting application package..."
cd ~

# Create a temporary extraction directory
EXTRACT_TMP=$(mktemp -d)
cd "$EXTRACT_TMP"
tar -xzf ~/{package_file}

# Find the extracted directory based on config
echo "🔍 Looking for extracted directories..."
ls -la

{dir_checks}

# Deploy files to target directory
sudo mkdir -p {target_dir}

if [ -n "$EXTRACTED_DIR" ]; then
    echo "✅ Found extracted directory: $EXTRACTED_DIR"
    echo "📋 Contents of $EXTRACTED_DIR:"
    ls -la "$EXTRACTED_DIR" | head -20
    
    # Check if this is a React app with build directory
    if [ -d "$EXTRACTED_DIR/build" ]; then
        echo "React build directory detected, deploying build files..."
        sudo cp -r "$EXTRACTED_DIR/build"/* {target_dir}/ || true
    else
        # Copy contents of the extracted directory
        echo "📦 Copying $EXTRACTED_DIR/* to {target_dir}/"
        sudo cp -r "$EXTRACTED_DIR"/* {target_dir}/ || true
    fi
else
    echo "⚠️  No wrapper directory found (example-*-app), checking for direct files"
    echo "📋 Current directory contents:"
    ls -la | head -20
    
    # Check if this looks like a Node.js app (has package.json at root)
    if [ -f "package.json" ]; then
        echo "✅ Node.js application detected (package.json at root), deploying all files..."
        sudo cp -r * {target_dir}/ || true
    # Check if this looks like a React build (has index.html and static directory)
    elif [ -f "index.html" ] && [ -d "static" ]; then
        echo "✅ React build files detected (index.html + static/), deploying directly..."
        sudo cp -r * {target_dir}/ || true
    # Check if build directory exists at root level
    elif [ -d "build" ]; then
        echo "Build directory detected at root, deploying build files..."
        sudo cp -r build/* {target_dir}/ || true
    # Check if this looks like a Python app (has requirements.txt or app.py)
    elif [ -f "requirements.txt" ] || [ -f "app.py" ] || [ -f "main.py" ]; then
        echo "✅ Python application detected, deploying all files..."
        sudo cp -r * {target_dir}/ || true
    # Check if this looks like a PHP app (has index.php)
    elif [ -f "index.php" ]; then
        echo "✅ PHP application detected, deploying all files..."
        sudo cp -r * {target_dir}/ || true
    else
        # Copy all files directly as fallback
        echo "📦 Copying all files to {target_dir}/"
        sudo cp -r * {target_dir}/ || true
    fi
fi

# Cleanup temp directory
cd ~
rm -rf "$EXTRACT_TMP"

# Verify files were copied
echo ""
echo "📋 Files in {target_dir} after deployment:"
ls -la {target_dir}/ | head -20

# Set proper ownership
'''
        
        # Get appropriate owner for this deployment
        owner = self._get_file_owner(target_dir)
        
        # Get OS-specific user information for web user check
        os_type = getattr(self.client, 'os_type', 'ubuntu')
        user_info = OSDetector.get_user_info(os_type, self.web_server)
        web_user = user_info['web_user']
        web_group = user_info['web_group']
        web_owner = f"{web_user}:{web_group}"
        
        script += f'''
echo "📝 Setting file permissions ({owner})"
sudo chown -R {owner} {target_dir}
sudo chmod -R 755 {target_dir}

# Set stricter permissions for web-served files
if [ "{owner}" = "{web_owner}" ]; then
    sudo find {target_dir} -type f -exec chmod 644 {{}} \\;
fi

echo "✅ Set ownership to {owner}"
'''
        
        script += '''
echo "✅ Application files deployed successfully"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        return success

    def _configure_application(self) -> bool:
        """Configure application based on installed dependencies using modular configurators"""
        print(f"🔍 Detected installed dependencies: {self.dependency_manager.installed_dependencies}")
        
        # Create configurators based on installed dependencies
        configurators = ConfiguratorFactory.create_configurators(
            self.client,
            self.config,
            self.dependency_manager.installed_dependencies
        )
        
        if not configurators:
            print("ℹ️  No configurators needed for this deployment")
            return True
        
        print(f"📋 Running {len(configurators)} configurator(s)...")
        
        # Run each configurator
        success = True
        for configurator in configurators:
            configurator_name = configurator.__class__.__name__
            print(f"\n🔧 Running {configurator_name}...")
            
            try:
                if not configurator.configure():
                    print(f"⚠️  {configurator_name} reported issues")
                    success = False
                else:
                    print(f"✅ {configurator_name} completed successfully")
            except Exception as e:
                print(f"❌ {configurator_name} failed with error: {str(e)}")
                success = False
        
        return success

    def _setup_app_specific_config(self) -> bool:
        """Set up application-specific configurations (OS-agnostic)"""
        app_type = self.config.get('application.type', 'web')
        
        # Get OS-specific user information
        os_type = getattr(self.client, 'os_type', 'ubuntu')
        user_info = OSDetector.get_user_info(os_type, self.web_server)
        default_user = user_info['default_user']
        
        script = f'''
set -e
echo "Setting up application-specific configurations..."

# Set up log rotation
cat > /tmp/app-logs << 'EOF'
/var/log/app/*.log {{
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 {default_user} {default_user}
}}
EOF

sudo mv /tmp/app-logs /etc/logrotate.d/app

# Create application log directory
sudo mkdir -p /var/log/app
sudo chown {default_user}:{default_user} /var/log/app

# Set up cron jobs for maintenance (if needed)
# This is a placeholder for application-specific maintenance tasks

echo "✅ Application-specific configurations completed"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _set_deployment_env_vars(self, env_vars):
        """Set deployment-specific environment variables (OS-agnostic)"""
        if not env_vars:
            return
        
        env_content = []
        for key, value in env_vars.items():
            env_content.append(f'{key}="{value}"')
        
        env_file_content = '\n'.join(env_content)
        
        # Get OS-specific user information
        os_type = getattr(self.client, 'os_type', 'ubuntu')
        user_info = OSDetector.get_user_info(os_type, self.web_server)
        web_user = user_info['web_user']
        web_group = user_info['web_group']
        
        script = f'''
set -e
echo "Setting deployment environment variables..."

# Ensure database configuration exists in .env file
if [ -f /opt/app/database.env ] && [ ! -f /var/www/html/.env ]; then
    echo "Copying database configuration to .env file..."
    sudo cp /opt/app/database.env /var/www/html/.env
    sudo chown {web_user}:{web_group} /var/www/html/.env
    sudo chmod 640 /var/www/html/.env
elif [ ! -f /var/www/html/.env ]; then
    # Create empty .env file if neither exists
    sudo touch /var/www/html/.env
    sudo chown {web_user}:{web_group} /var/www/html/.env
    sudo chmod 640 /var/www/html/.env
fi

# Create temporary file with deployment variables
cat > /tmp/deployment_vars << 'EOF'

# Deployment Variables
{env_file_content}
EOF

# Append deployment vars to existing .env file using sudo
sudo bash -c 'cat /tmp/deployment_vars >> /var/www/html/.env'
sudo rm -f /tmp/deployment_vars

echo "✅ Deployment environment variables set"
'''
        
        success, output = self.client.run_command(script, timeout=30)

    def _run_pm2_post_setup_script(self) -> bool:
        """Run PM2 post-setup script if specified"""
        post_script = self.config.get_pm2_post_setup_script()
        if not post_script:
            return True
        
        print(f"🔧 Running PM2 post-setup script: {post_script}")
        
        # Get target directory where application is deployed
        target_dir = self._get_target_directory()
        
        script = f'''
set -e
echo "Running PM2 post-setup script: {post_script}"

# Change to application directory
cd {target_dir}

# Check if script exists
if [ ! -f "{post_script}" ]; then
    echo "❌ PM2 post-setup script not found: {post_script}"
    exit 1
fi

# Make script executable
chmod +x {post_script}

# Run the script
echo "🚀 Executing {post_script}..."
./{post_script}

echo "✅ PM2 post-setup script completed successfully"
'''
        
        success, output = self.client.run_command(script, timeout=600)
        print(output)
        
        if not success:
            print(f"❌ PM2 post-setup script failed: {post_script}")
            return False
        
        print(f"✅ PM2 post-setup script completed: {post_script}")
        return True

    def _verify_deployment(self) -> bool:
        """Verify that the deployment was successful"""
        health_config = self.config.get_health_check_config()
        endpoint = health_config.get('endpoint', '/')
        expected_content = health_config.get('expected_content', 'Hello')
        
        script = f'''
set -e
echo "Verifying deployment..."

# Check if application services are running
for service in nodejs-app python-app; do
    if systemctl list-unit-files | grep -q "^${{service}}.service"; then
        if systemctl is-active --quiet ${{service}}.service; then
            echo "✅ ${{service}} service is running"
        else
            echo "⚠️  ${{service}} service is not running"
        fi
    fi
done

# Check if web server is running
if systemctl is-active --quiet apache2; then
    echo "✅ Apache is running"
elif systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "⚠️  No web server detected as running"
fi

# Check if application files exist in common locations
if [ -d "/opt/nodejs-app" ] && [ -n "$(ls -A /opt/nodejs-app 2>/dev/null)" ]; then
    echo "✅ Node.js application files found"
elif [ -d "/opt/python-app" ] && [ -n "$(ls -A /opt/python-app 2>/dev/null)" ]; then
    echo "✅ Python application files found"
elif [ -d "/opt/docker-app" ] && [ -n "$(ls -A /opt/docker-app 2>/dev/null)" ]; then
    echo "✅ Docker application files found"
elif [ -f "/var/www/html/index.php" ] || [ -f "/var/www/html/index.html" ]; then
    echo "✅ Web application files found"
else
    echo "⚠️  No main application files found"
fi

# Test local HTTP response
echo "Testing local HTTP response..."
for i in {{1..5}}; do
    if curl -s http://localhost{endpoint} | grep -q "{expected_content}"; then
        echo "✅ Application responds correctly"
        exit 0
    fi
    echo "Waiting for application to respond... ($i/5)"
    sleep 2
done

echo "⚠️  Application response test failed after 5 attempts"
curl -v http://localhost{endpoint} || true

echo "✅ Deployment verification completed"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _cleanup_deployment(self):
        """Clean up temporary deployment files"""
        script = '''
set -e
echo "Cleaning up deployment files..."

# Remove temporary files
sudo rm -f /tmp/*.tar.gz
sudo rm -f /tmp/app.*
sudo rm -rf /tmp/deployment_*

# Clean package manager caches
sudo apt-get clean || true

echo "✅ Cleanup completed"
'''
        
        success, output = self.client.run_command(script, timeout=60)

    def _optimize_performance(self):
        """Optimize system and application performance"""
        script = '''
set -e
echo "🔧 Starting performance optimization..."

# Optimize web servers if running
for webserver in apache2 nginx; do
    if systemctl is-active --quiet $webserver 2>/dev/null; then
        echo "⚡ Optimizing $webserver web server..."
        if [ "$webserver" = "apache2" ]; then
            sudo a2enmod deflate 2>/dev/null || true
            sudo a2enmod expires 2>/dev/null || true
            sudo a2enmod headers 2>/dev/null || true
            sudo systemctl reload apache2 2>/dev/null || true
        fi
        echo "✅ $webserver performance optimized"
    fi
done

# Optimize PHP if installed
if which php > /dev/null 2>&1; then
    echo "⚡ Optimizing PHP configuration..."
    for PHP_INI in /etc/php/*/apache2/php.ini /etc/php/*/fpm/php.ini; do
        if [ -f "$PHP_INI" ]; then
            sudo sed -i 's/;opcache.enable=1/opcache.enable=1/' "$PHP_INI" 2>/dev/null || true
            sudo sed -i 's/;opcache.memory_consumption=128/opcache.memory_consumption=128/' "$PHP_INI" 2>/dev/null || true
            sudo sed -i 's/;opcache.max_accelerated_files=4000/opcache.max_accelerated_files=10000/' "$PHP_INI" 2>/dev/null || true
            sudo sed -i 's/;opcache.revalidate_freq=2/opcache.revalidate_freq=60/' "$PHP_INI" 2>/dev/null || true
        fi
    done
    echo "✅ PHP performance optimized"
fi

# System-level optimizations
echo "⚡ Applying system-level optimizations..."
sudo sysctl -w vm.swappiness=10 || true
sudo sysctl -w net.core.rmem_max=16777216 || true
sudo sysctl -w net.core.wmem_max=16777216 || true

# Clear system caches
echo "🧹 Clearing system caches..."
sudo apt-get clean || true
sudo apt-get autoremove -y || true

echo "✅ Performance optimization completed successfully"
'''
        
        success, output = self.client.run_command(script, timeout=60)
    
    def _print_deployment_summary(self):
        """Print deployment summary information"""
        print("\n" + "="*60)
        print("📊 DEPLOYMENT SUMMARY")
        print("="*60)
        
        # Get instance info
        instance_info = self.client.get_instance_info()
        if instance_info:
            print(f"🖥️  Instance Name: {instance_info['name']}")
            print(f"🌐 Public IP: {instance_info.get('public_ip', 'N/A')}")
            print(f"🔒 Private IP: {instance_info.get('private_ip', 'N/A')}")
            print(f"📦 Blueprint: {instance_info.get('blueprint', 'N/A')}")
            print(f"💾 Bundle: {instance_info.get('bundle', 'N/A')}")
            print(f"⚡ State: {instance_info.get('state', 'N/A')}")
        
        # Show installed dependencies
        if hasattr(self.dependency_manager, 'installed_dependencies'):
            installed = self.dependency_manager.installed_dependencies
            if installed:
                print(f"\n🔧 Installed Dependencies ({len(installed)}):")
                for dep in installed:
                    print(f"   ✅ {dep}")
        
        # Show application configuration
        app_config = {
            'Name': self.config.get('application.name', 'Generic Application'),
            'Version': self.config.get('application.version', '1.0.0'),
            'Type': self.config.get('application.type', 'web'),
            'PHP Version': self.config.get('application.php_version', '8.1'),
        }
        
        print(f"\n📋 Application Configuration:")
        for key, value in app_config.items():
            print(f"   {key}: {value}")
        
        print("\n🎯 Next Steps:")
        if instance_info and instance_info.get('public_ip'):
            print(f"   🌐 Visit: http://{instance_info['public_ip']}")
        
        # Show relevant log locations based on what's installed
        log_locations = []
        if 'apache' in installed:
            log_locations.append("/var/log/apache2/")
        if 'nginx' in installed:
            log_locations.append("/var/log/nginx/")
        if 'nodejs' in installed:
            log_locations.append("/var/log/nodejs-app/")
        if 'python' in installed:
            log_locations.append("/var/log/python-app/")
        
        if log_locations:
            print(f"   📝 Check logs: {', '.join(log_locations)}")
        
        # Show relevant config locations
        config_locations = []
        if 'apache' in installed or 'nginx' in installed:
            config_locations.append("/var/www/html/.env")
        if 'nodejs' in installed:
            config_locations.append("/opt/nodejs-app/")
        if 'python' in installed:
            config_locations.append("/opt/python-app/")
        
        if config_locations:
            print(f"   🔧 Config files: {', '.join(config_locations)}")
        
        # Show relevant services to monitor
        services = []
        if 'apache' in installed:
            services.append("apache2")
        if 'nginx' in installed:
            services.append("nginx")
        if 'mysql' in installed:
            services.append("mysql")
        if 'postgresql' in installed:
            services.append("postgresql")
        if 'nodejs' in installed:
            services.append("nodejs-app")
        if 'python' in installed:
            services.append("python-app")
        if 'docker' in installed:
            services.append("docker")
        
        if services:
            print(f"   📊 Monitor: systemctl status {' '.join(services)}")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Generic post-deployment steps for AWS Lightsail')
    parser.add_argument('package_file', help='Application package file to deploy')
    parser.add_argument('--instance-name', help='Lightsail instance name (overrides config)')
    parser.add_argument('--region', help='AWS region (overrides config)')
    parser.add_argument('--config-file', help='Path to configuration file')
    parser.add_argument('--verify', action='store_true', help='Verify deployment')
    parser.add_argument('--cleanup', action='store_true', help='Clean up temporary files')
    parser.add_argument('--env', action='append', help='Environment variables (KEY=VALUE)')
    parser.add_argument('--os-type', help='Operating system type (ubuntu, amazon_linux, centos, rhel)')
    parser.add_argument('--package-manager', help='Package manager (apt, yum, dnf)')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config_file = args.config_file if args.config_file else 'deployment-generic.config.yml'
        config = DeploymentConfig(config_file=config_file)
        
        # Use command line args if provided, otherwise use config
        instance_name = args.instance_name or config.get_instance_name()
        region = args.region or config.get_aws_region()
        
        print(f"🚀 Starting generic post-deployment steps for {instance_name}")
        print(f"🌍 Region: {region}")
        print(f"📦 Package: {args.package_file}")
        print(f"📋 Application: {config.get('application.name', 'Unknown')} v{config.get('application.version', '1.0.0')}")
        print(f"🏷️  Type: {config.get('application.type', 'web')}")
        
        # Parse environment variables
        env_vars = {}
        if args.env:
            for env_var in args.env:
                if '=' in env_var:
                    key, value = env_var.split('=', 1)
                    env_vars[key] = value
        
        # Check if dependency steps are enabled in config
        if not config.get('deployment.steps.post_deployment.dependencies.enabled', True):
            print("ℹ️  Dependency configuration steps are disabled in configuration")
        
        # Create generic post-deployer and deploy application
        post_deployer = GenericPostDeployer(
            instance_name, 
            region, 
            config, 
            os_type=args.os_type, 
            package_manager=args.package_manager
        )
        
        if post_deployer.deploy_application(
            args.package_file, 
            verify=args.verify, 
            cleanup=args.cleanup,
            env_vars=env_vars
        ):
            # Print deployment summary
            post_deployer._print_deployment_summary()
            print("🎉 Generic post-deployment steps completed successfully!")
            sys.exit(0)
        else:
            print("❌ Generic post-deployment steps failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error in generic post-deployment steps: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
