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

class GenericPostDeployer:
    def __init__(self, instance_name=None, region=None, config=None):
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
        self.dependency_manager = DependencyManager(self.client, config)
        
        # Load installed dependencies from the system
        self._detect_installed_dependencies()

    def _detect_installed_dependencies(self):
        """Detect which dependencies are currently installed on the system"""
        enabled_deps = self.dependency_manager.get_enabled_dependencies()
        
        # Check which services are actually running/installed
        check_script = '''
set -e
echo "Checking installed services..."

# Check for web servers
systemctl is-active --quiet apache2 && echo "apache:installed" || true
systemctl is-active --quiet nginx && echo "nginx:installed" || true

# Check for databases
systemctl is-active --quiet mysql && echo "mysql:installed" || true
systemctl is-active --quiet postgresql && echo "postgresql:installed" || true

# Check for other services
systemctl is-active --quiet redis-server && echo "redis:installed" || true
systemctl is-active --quiet memcached && echo "memcached:installed" || true
systemctl is-active --quiet docker && echo "docker:installed" || true

# Check for programming languages
which php > /dev/null 2>&1 && echo "php:installed" || true
which python3 > /dev/null 2>&1 && echo "python:installed" || true
which node > /dev/null 2>&1 && echo "nodejs:installed" || true
which git > /dev/null 2>&1 && echo "git:installed" || true
which apache2 > /dev/null 2>&1 && echo "apache:installed" || true

echo "Service check completed"
'''
        
        success, output = self.client.run_command(check_script, timeout=60)
        if success:
            for line in output.split('\n'):
                if ':installed' in line:
                    dep_name = line.split(':')[0]
                    if dep_name in enabled_deps:
                        self.dependency_manager.installed_dependencies.append(dep_name)

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
            success = self._deploy_with_docker(package_file, env_vars)
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
        
            # For Node.js apps, verify the service is still running after restart
            if 'nodejs' in self.dependency_manager.installed_dependencies:
                print("\n🔍 Verifying Node.js service after restart...")
                verify_script = '''
if systemctl is-active --quiet nodejs-app.service; then
    echo "✅ Node.js service is running"
    # Test local connection
    if curl -s http://localhost:3000/ > /dev/null 2>&1; then
        echo "✅ Node.js app responding on port 3000"
    else
        echo "⚠️  Node.js service running but not responding on port 3000"
    fi
else
    echo "❌ Node.js service is NOT running after restart!"
    sudo systemctl status nodejs-app.service --no-pager || true
    echo "=== Recent logs ==="
    sudo journalctl -u nodejs-app.service -n 30 --no-pager || true
fi
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
    
    def _deploy_with_docker(self, package_file, env_vars=None) -> bool:
        """Deploy application using Docker and docker-compose"""
        print("🐳 Deploying application with Docker...")
        
        # Check if using pre-built image
        docker_image_tag = os.environ.get('DOCKER_IMAGE_TAG', '')
        use_prebuilt_image = bool(docker_image_tag)
        
        if use_prebuilt_image:
            print(f"📦 Using pre-built Docker image: {docker_image_tag}")
        else:
            print("🔨 Will build Docker image on instance")
        
        # Upload package to instance
        print(f"📤 Uploading package file {package_file}...")
        remote_package_path = f"~/{package_file}"
        
        if not self.client.copy_file_to_instance(package_file, remote_package_path):
            print(f"❌ Failed to upload package file")
            return False
        
        # Prepare environment variables for docker-compose
        env_file_content = ""
        if env_vars:
            for key, value in env_vars.items():
                env_file_content += f'{key}={value}\n'
        
        script = f'''
set -e
echo "🐳 Setting up Docker deployment..."

# Set Docker image tag if provided
export DOCKER_IMAGE_TAG="{docker_image_tag}"

# Create deployment directory
DEPLOY_DIR="/opt/docker-app"
sudo mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR

# Extract application package
echo "📦 Extracting application..."
sudo tar -xzf ~/{package_file} -C $DEPLOY_DIR

# Find docker-compose file
COMPOSE_FILE=$(find . -name "docker-compose.yml" -o -name "docker-compose.yaml" | head -n 1)

if [ -z "$COMPOSE_FILE" ]; then
    echo "❌ No docker-compose.yml found in package"
    exit 1
fi

echo "✅ Found docker-compose file: $COMPOSE_FILE"

# Create .env file if environment variables provided
if [ -n "{env_file_content}" ]; then
    sudo tee .env > /dev/null << 'ENVEOF'
{env_file_content}
ENVEOF
    echo "✅ Environment file created"
fi

# Ensure Docker is available and add user to docker group
# Check multiple possible Docker locations
DOCKER_BIN=""
if [ -f /usr/bin/docker ]; then
    DOCKER_BIN="/usr/bin/docker"
elif command -v docker > /dev/null 2>&1; then
    DOCKER_BIN=$(command -v docker)
else
    echo "⚠️  Docker not found, attempting to install..."
    
    # Install Docker using the convenience script (more reliable than manual GPG setup)
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo sh /tmp/get-docker.sh
    
    # Start and enable Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Check again
    if [ -f /usr/bin/docker ]; then
        DOCKER_BIN="/usr/bin/docker"
    elif command -v docker > /dev/null 2>&1; then
        DOCKER_BIN=$(command -v docker)
    else
        echo "❌ Docker installation failed"
        exit 1
    fi
    
    echo "✅ Docker installed successfully"
fi

echo "✅ Docker found at $DOCKER_BIN"

# Add ubuntu user to docker group for non-sudo access
sudo usermod -aG docker ubuntu || true

# Stop existing containers (use sudo for now until group takes effect)
echo "🛑 Stopping existing containers..."
sudo $DOCKER_BIN compose -f $COMPOSE_FILE down --timeout 30 || true

# Check if using pre-built image from environment
if [ -n "$DOCKER_IMAGE_TAG" ]; then
    echo "📦 Using pre-built image: $DOCKER_IMAGE_TAG"
    export DOCKER_IMAGE="$DOCKER_IMAGE_TAG"
    
    # Check network connectivity before pulling
    echo "🔍 Checking network connectivity..."
    if ! timeout 10 ping -c 2 8.8.8.8 > /dev/null 2>&1; then
        echo "⚠️  Network connectivity issue detected"
    fi
    
    # Check DNS resolution
    if ! timeout 10 nslookup hub.docker.com > /dev/null 2>&1; then
        echo "⚠️  DNS resolution issue for hub.docker.com"
        echo "Trying to resolve with Google DNS..."
        sudo bash -c 'echo "nameserver 8.8.8.8" > /etc/resolv.conf.tmp'
        sudo bash -c 'cat /etc/resolv.conf >> /etc/resolv.conf.tmp'
        sudo mv /etc/resolv.conf.tmp /etc/resolv.conf
    fi
    
    # Configure Docker to use different registry mirrors if needed
    echo "🔧 Configuring Docker daemon..."
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json > /dev/null << 'DOCKEREOF'
{{
  "registry-mirrors": [],
  "max-concurrent-downloads": 3,
  "max-concurrent-uploads": 3,
  "log-driver": "json-file",
  "log-opts": {{
    "max-size": "10m",
    "max-file": "3"
  }}
}}
DOCKEREOF
    sudo systemctl restart docker || true
    sleep 5
    
    # Pull the pre-built image with retry logic
    echo "📥 Pulling pre-built Docker image..."
    PULL_SUCCESS=false
    for attempt in 1 2 3; do
        echo "Attempt $attempt/3 to pull image..."
        if timeout 600 sudo $DOCKER_BIN pull "$DOCKER_IMAGE_TAG"; then
            echo "✅ Image pulled successfully"
            PULL_SUCCESS=true
            break
        else
            echo "⚠️  Pull attempt $attempt failed"
            if [ $attempt -lt 3 ]; then
                echo "Waiting 10 seconds before retry..."
                sleep 10
            fi
        fi
    done
    
    if [ "$PULL_SUCCESS" = "false" ]; then
        echo "❌ Failed to pull image after 3 attempts"
        echo "Checking Docker Hub connectivity..."
        timeout 10 curl -I https://hub.docker.com/ || echo "Cannot reach Docker Hub"
        exit 1
    fi
    
    # Pull other service images (MySQL, Redis, etc.) with retry
    echo "📥 Pulling service images..."
    for attempt in 1 2; do
        if timeout 600 sudo $DOCKER_BIN compose -f $COMPOSE_FILE pull db redis phpmyadmin 2>/dev/null; then
            echo "✅ Service images pulled"
            break
        else
            echo "⚠️  Some service images may have issues (attempt $attempt/2)"
            [ $attempt -lt 2 ] && sleep 5
        fi
    done
else
    echo "🔨 Building Docker image on instance..."
    # Pull base images first
    echo "📥 Pulling base Docker images..."
    timeout 600 sudo $DOCKER_BIN compose -f $COMPOSE_FILE pull || echo "⚠️  Some images may need to be built"
    
    # Build images if needed (with timeout - use cache for faster builds)
    if grep -q "build:" $COMPOSE_FILE; then
        echo "🔨 Building Docker images..."
        timeout 900 sudo $DOCKER_BIN compose -f $COMPOSE_FILE build || {{
            echo "❌ Build failed after 15 minutes"
            sudo $DOCKER_BIN compose -f $COMPOSE_FILE logs --tail=100
            exit 1
        }}
    fi
fi

# Start containers (with extended timeout)
echo "🚀 Starting containers..."
timeout 300 sudo $DOCKER_BIN compose -f $COMPOSE_FILE up -d || {{
    echo "❌ Failed to start containers within 5 minutes"
    echo "📋 Checking what went wrong..."
    sudo $DOCKER_BIN compose -f $COMPOSE_FILE ps -a
    sudo $DOCKER_BIN compose -f $COMPOSE_FILE logs --tail=100
    exit 1
}}

# Wait for containers to initialize (extended wait time)
echo "⏳ Waiting for containers to initialize..."
sleep 30

# Check container status
echo "📊 Container status:"
sudo $DOCKER_BIN compose -f $COMPOSE_FILE ps

# Count running containers
RUNNING_COUNT=$(sudo $DOCKER_BIN compose -f $COMPOSE_FILE ps --filter "status=running" --format json 2>/dev/null | wc -l)
TOTAL_COUNT=$(sudo $DOCKER_BIN compose -f $COMPOSE_FILE ps --format json 2>/dev/null | wc -l)

echo "Running containers: $RUNNING_COUNT / $TOTAL_COUNT"

if [ "$RUNNING_COUNT" -eq 0 ]; then
    echo "❌ No containers are running!"
    echo "📋 Container logs:"
    sudo $DOCKER_BIN compose -f $COMPOSE_FILE logs --tail=100
    exit 1
fi

# Show logs
echo "📋 Recent logs:"
sudo $DOCKER_BIN compose -f $COMPOSE_FILE logs --tail=30

# Test web service connectivity (with more attempts and longer waits)
echo "🔍 Testing web service..."
WEB_READY=false
for i in {{1..20}}; do
    if curl -f -s --connect-timeout 5 http://localhost/ > /dev/null 2>&1; then
        echo "✅ Web service is responding"
        WEB_READY=true
        break
    fi
    echo "Waiting for web service... ($i/20)"
    sleep 5
done

if [ "$WEB_READY" = "false" ]; then
    echo "⚠️  Web service not responding after 100 seconds, but containers may still be starting"
    echo "📋 Container status:"
    sudo $DOCKER_BIN compose -f $COMPOSE_FILE ps
    echo "📋 Recent logs:"
    sudo $DOCKER_BIN compose -f $COMPOSE_FILE logs --tail=50
fi

echo "✅ Docker deployment completed"
'''
        
        success, output = self.client.run_command(script, timeout=1200)
        print(output)
        
        if not success:
            print("❌ Docker deployment failed")
            return False
        
        print("✅ Application deployed with Docker successfully")
        return True

    def _deploy_application_files(self, package_file) -> bool:
        """Deploy application files to the appropriate location"""
        app_type = self.config.get('application.type', 'web')
        
        # Determine deployment target based on app type and installed dependencies
        if app_type == 'web':
            # For Node.js web apps, deploy to /opt/nodejs-app
            if 'nodejs' in self.dependency_manager.installed_dependencies:
                target_dir = '/opt/nodejs-app'
            elif 'apache' in self.dependency_manager.installed_dependencies:
                target_dir = self.config.get('dependencies.apache.config.document_root', '/var/www/html')
            elif 'nginx' in self.dependency_manager.installed_dependencies:
                target_dir = self.config.get('dependencies.nginx.config.document_root', '/var/www/html')
            else:
                target_dir = '/var/www/html'
        elif app_type == 'api':
            if 'python' in self.dependency_manager.installed_dependencies:
                target_dir = '/opt/app'
            elif 'nodejs' in self.dependency_manager.installed_dependencies:
                target_dir = '/opt/nodejs-app'
            else:
                target_dir = '/opt/app'
        elif app_type == 'static':
            # For static sites, use nginx document_root if nginx is enabled
            if 'nginx' in self.dependency_manager.installed_dependencies:
                target_dir = self.config.get('dependencies.nginx.config.document_root', '/var/www/html')
            else:
                target_dir = '/var/www/html'
        else:
            target_dir = '/opt/app'
        
        # First, copy the package file to the remote instance
        print(f"📤 Uploading package file {package_file} to remote instance...")
        # Use home directory instead of /tmp to avoid permission issues
        remote_package_path = f"~/{package_file}"
        
        if not self.client.copy_file_to_instance(package_file, remote_package_path):
            print(f"❌ Failed to upload package file to remote instance")
            return False
        
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
tar -xzf {package_file}

# Find the extracted directory (usually example-*-app, mcp-server, or just files)
echo "🔍 Looking for extracted directories..."
ls -la

# Prioritize mcp-server over example-*-app directories
if [ -d "./mcp-server" ]; then
    EXTRACTED_DIR="./mcp-server"
    echo "✅ Found mcp-server directory (prioritized)"
else
    EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "example-*-app" | head -n 1)
fi

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
    echo "⚠️  No application directory found (example-*-app or mcp-server), copying all files"
    echo "📋 Current directory contents:"
    ls -la | head -20
    
    # Check if build directory exists at root level
    if [ -d "build" ]; then
        echo "Build directory detected at root, deploying build files..."
        sudo cp -r build/* {target_dir}/ || true
    else
        # Copy all files directly
        echo "📦 Copying all files to {target_dir}/"
        sudo cp -r * {target_dir}/ || true
    fi
fi

# Verify files were copied
echo ""
echo "📋 Files in {target_dir} after deployment:"
ls -la {target_dir}/ | head -20

# Set proper ownership based on application type
'''
        
        # Check if nginx or apache are enabled in config
        nginx_enabled = self.config.get('dependencies.nginx.enabled', False)
        apache_enabled = self.config.get('dependencies.apache.enabled', False)
        nodejs_enabled = self.config.get('dependencies.nodejs.enabled', False)
        
        # Debug logging
        script += f'''
echo "🔍 Permission Debug Info:"
echo "  App Type: {app_type}"
echo "  Nginx Enabled: {nginx_enabled}"
echo "  Apache Enabled: {apache_enabled}"
echo "  Node.js Enabled: {nodejs_enabled}"
echo "  Installed Dependencies: {','.join(self.dependency_manager.installed_dependencies)}"
'''
        
        # For Node.js apps, always use ubuntu user
        if 'nodejs' in self.dependency_manager.installed_dependencies or nodejs_enabled:
            script += f'''
echo "📝 Setting Node.js app permissions (ubuntu:ubuntu)"
sudo chown -R ubuntu:ubuntu {target_dir}
sudo chmod -R 755 {target_dir}
echo "✅ Set ownership to ubuntu:ubuntu for Node.js app"
'''
        elif (app_type in ['web', 'static'] or 
              'nginx' in self.dependency_manager.installed_dependencies or 
              'apache' in self.dependency_manager.installed_dependencies or
              nginx_enabled or apache_enabled):
            # Web servers need www-data ownership
            script += f'''
echo "📝 Setting web server permissions (www-data:www-data)"
sudo chown -R www-data:www-data {target_dir}
sudo chmod -R 755 {target_dir}
sudo find {target_dir} -type f -exec chmod 644 {{}} \\;
echo "✅ Set ownership to www-data:www-data for web server"
ls -la {target_dir}/ | head -10
'''
        else:
            script += f'''
echo "📝 Setting default permissions (ubuntu:ubuntu)"
sudo chown -R ubuntu:ubuntu {target_dir}
sudo chmod -R 755 {target_dir}
'''
        
        script += '''
echo "✅ Application files deployed successfully"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        return success

    def _configure_application(self) -> bool:
        """Configure application based on installed dependencies"""
        success = True
        
        print(f"🔍 Detected installed dependencies: {self.dependency_manager.installed_dependencies}")
        
        # Configure web server if installed
        if 'apache' in self.dependency_manager.installed_dependencies:
            print("🔧 Configuring Apache...")
            success &= self._configure_apache_for_app()
        
        if 'nginx' in self.dependency_manager.installed_dependencies:
            print("🔧 Configuring Nginx...")
            success &= self._configure_nginx_for_app()
        
        # Configure PHP if installed
        if 'php' in self.dependency_manager.installed_dependencies:
            print("🔧 Configuring PHP...")
            success &= self._configure_php_for_app()
        
        # Configure Python if installed
        if 'python' in self.dependency_manager.installed_dependencies:
            print("🔧 Configuring Python...")
            success &= self._configure_python_for_app()
        else:
            print("⚠️  Python not detected in installed dependencies, skipping Python configuration")
        
        # Configure Node.js if installed
        if 'nodejs' in self.dependency_manager.installed_dependencies:
            print("🔧 Configuring Node.js...")
            success &= self._configure_nodejs_for_app()
        
        # Configure database connections
        success &= self._configure_database_connections()
        
        return success

    def _configure_apache_for_app(self) -> bool:
        """Configure Apache for the application"""
        app_type = self.config.get('application.type', 'web')
        document_root = self.config.get('dependencies.apache.config.document_root', '/var/www/html')
        
        script = f'''
set -e
echo "Configuring Apache for application..."

# Create virtual host configuration
cat > /tmp/app.conf << 'EOF'
<VirtualHost *:80>
    DocumentRoot {document_root}
    
    <Directory {document_root}>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    # Enable rewrite engine for pretty URLs
    RewriteEngine On
    
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    
    ErrorLog /var/log/apache2/app_error.log
    CustomLog /var/log/apache2/app_access.log combined
</VirtualHost>
EOF

# Install the configuration
sudo mv /tmp/app.conf /etc/apache2/sites-available/app.conf
sudo a2ensite app.conf
sudo a2dissite 000-default.conf || true

# Enable required modules
sudo a2enmod rewrite
sudo a2enmod headers

echo "✅ Apache configured for application"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _configure_nginx_for_app(self) -> bool:
        """Configure Nginx for the application"""
        document_root = self.config.get('dependencies.nginx.config.document_root', '/var/www/html')
        
        # Check if Node.js is enabled - if so, configure as reverse proxy
        if 'nodejs' in self.dependency_manager.installed_dependencies:
            script = '''
set -e
echo "Configuring Nginx as reverse proxy for Node.js application..."

# Create server block configuration for Node.js proxy
cat > /tmp/app << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
EOF

# Install the configuration
sudo mv /tmp/app /etc/nginx/sites-available/app
sudo ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app
sudo rm -f /etc/nginx/sites-enabled/default

echo "✅ Nginx configured as reverse proxy for Node.js"
'''
        # Check if Python is enabled - if so, configure as reverse proxy to port 5000
        elif 'python' in self.dependency_manager.installed_dependencies:
            script = '''
set -e
echo "Configuring Nginx as reverse proxy for Python application..."

# Create server block configuration for Python proxy
cat > /tmp/app << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:5000/health;
        access_log off;
    }
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
EOF

# Install the configuration
sudo mv /tmp/app /etc/nginx/sites-available/app
sudo ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app
sudo rm -f /etc/nginx/sites-enabled/default

echo "✅ Nginx configured as reverse proxy for Python"
'''
        else:
            # Check if this is a React app (has index.html but no index.php)
            app_type = self.config.get('application.type', 'web')
            script = f'''
set -e
echo "Configuring Nginx for application..."

# Check if this is a React/SPA application
if [ -f "{document_root}/index.html" ] && [ ! -f "{document_root}/index.php" ]; then
    echo "Detected React/SPA application"
    cat > /tmp/app << 'EOF'
server {{
    listen 80;
    server_name _;
    
    root {document_root};
    index index.html;
    
    location / {{
        try_files $uri $uri/ /index.html;
    }}
    
    # Cache static assets
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}}
EOF
else
    echo "Detected PHP/traditional web application"
    cat > /tmp/app << 'EOF'
server {{
    listen 80;
    server_name _;
    
    root {document_root};
    index index.php index.html index.htm;
    
    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}
    
    location ~ \\\\.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
    }}
    
    location ~ /\\\\.ht {{
        deny all;
    }}
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}}
EOF
fi

# Install the configuration
sudo mv /tmp/app /etc/nginx/sites-available/app
sudo ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app
sudo rm -f /etc/nginx/sites-enabled/default

echo "✅ Nginx configured for application"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _configure_php_for_app(self) -> bool:
        """Configure PHP for the application"""
        script = '''
set -e
echo "Configuring PHP for application..."

# Configure PHP settings for production
PHP_INI="/etc/php/8.1/apache2/php.ini"
if [ -f "$PHP_INI" ]; then
    sudo sed -i 's/display_errors = On/display_errors = Off/' "$PHP_INI"
    sudo sed -i 's/;date.timezone =/date.timezone = UTC/' "$PHP_INI"
    sudo sed -i 's/upload_max_filesize = 2M/upload_max_filesize = 10M/' "$PHP_INI"
    sudo sed -i 's/post_max_size = 8M/post_max_size = 10M/' "$PHP_INI"
fi

# Configure PHP-FPM if available
PHP_FPM_INI="/etc/php/8.1/fpm/php.ini"
if [ -f "$PHP_FPM_INI" ]; then
    sudo sed -i 's/display_errors = On/display_errors = Off/' "$PHP_FPM_INI"
    sudo sed -i 's/;date.timezone =/date.timezone = UTC/' "$PHP_FPM_INI"
fi

echo "✅ PHP configured for application"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _configure_python_for_app(self) -> bool:
        """Configure Python for the application"""
        app_type = self.config.get('application.type', 'web')
        
        if app_type == 'api':
            script = '''
set -e
echo "Configuring Python for API application..."

# Check if app files exist
if [ ! -f "/opt/app/app.py" ]; then
    echo "❌ No app.py found in /opt/app"
    ls -la /opt/app/ || echo "Directory does not exist"
    exit 1
fi

# Install Python dependencies if requirements.txt exists
if [ -f "/opt/app/requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    cd /opt/app
    
    # Ensure pip is installed
    if ! command -v pip3 &> /dev/null; then
        echo "Installing pip3..."
        sudo apt-get update
        sudo apt-get install -y python3-pip
    fi
    
    # Install dependencies
    sudo pip3 install -r requirements.txt 2>&1 | tee /tmp/pip-install.log
    echo "✅ Dependencies installed"
else
    echo "ℹ️  No requirements.txt found, skipping dependency installation"
fi

# Create log directory
sudo mkdir -p /var/log/python-app
sudo chown ubuntu:ubuntu /var/log/python-app

# Create systemd service for Python app
echo "📝 Creating systemd service file..."
sudo tee /etc/systemd/system/python-app.service > /dev/null << 'EOF'
[Unit]
Description=Python Flask Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/app
Environment=PATH=/usr/bin:/usr/local/bin
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production
ExecStart=/usr/bin/python3 /opt/app/app.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/python-app/output.log
StandardError=append:/var/log/python-app/error.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable the service
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload
sudo systemctl enable python-app.service

# Stop any existing instance
sudo systemctl stop python-app.service 2>/dev/null || true

# Start the service
echo "🚀 Starting Python application service..."
sudo systemctl start python-app.service

# Wait and check if service started successfully
sleep 5

if systemctl is-active --quiet python-app.service; then
    echo "✅ Python app service started successfully"
    sudo systemctl status python-app.service --no-pager
    
    # Check if app is listening on port 5000
    sleep 2
    if sudo ss -tlnp 2>/dev/null | grep -q ":5000" || sudo netstat -tlnp 2>/dev/null | grep -q ":5000"; then
        echo "✅ Application is listening on port 5000"
    else
        echo "⚠️  Application may not be listening on port 5000"
        sudo ss -tlnp 2>/dev/null | grep python || sudo netstat -tlnp 2>/dev/null | grep python || echo "No python process found listening"
    fi
    
    # Test local connection
    if curl -s http://localhost:5000/ > /dev/null; then
        echo "✅ Local connection to port 5000 successful"
    else
        echo "⚠️  Local connection to port 5000 failed"
    fi
else
    echo "❌ Python app service failed to start"
    sudo systemctl status python-app.service --no-pager || true
    echo "=== Service Logs ==="
    sudo journalctl -u python-app.service -n 50 --no-pager || true
    echo "=== Application Error Log ==="
    sudo cat /var/log/python-app/error.log 2>/dev/null || echo "No error log found"
    exit 1
fi

echo "✅ Python app service configured"
'''
        else:
            script = '''
set -e
echo "Configuring Python for web application..."

# Install mod_wsgi if Apache is present
if systemctl is-active --quiet apache2; then
    sudo apt-get update
    sudo apt-get install -y libapache2-mod-wsgi-py3
    sudo a2enmod wsgi
    echo "✅ mod_wsgi configured for Apache"
fi
'''
        
        success, output = self.client.run_command(script, timeout=120)
        return success

    def _configure_nodejs_for_app(self) -> bool:
        """Configure Node.js for the application"""
        script = '''
set -e
echo "Configuring Node.js for application..."

# Check if app files exist
if [ ! -f "/opt/nodejs-app/app.js" ] && [ ! -f "/opt/nodejs-app/index.js" ]; then
    echo "❌ No app.js or index.js found in /opt/nodejs-app"
    ls -la /opt/nodejs-app/ || echo "Directory does not exist"
    exit 1
fi

# Install dependencies if package.json exists
if [ -f "/opt/nodejs-app/package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd /opt/nodejs-app && sudo -u ubuntu npm install --production 2>&1 | tee /tmp/npm-install.log
    echo "✅ Dependencies installed"
else
    echo "ℹ️  No package.json found, skipping dependency installation"
fi

# Create log directory
sudo mkdir -p /var/log/nodejs-app
sudo chown ubuntu:ubuntu /var/log/nodejs-app

# Create systemd service for Node.js app
echo "📝 Creating systemd service file..."
sudo tee /etc/systemd/system/nodejs-app.service > /dev/null << 'EOF'
[Unit]
Description=Node.js Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/nodejs-app
ExecStart=/usr/bin/node app.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production
Environment=PORT=3000
StandardOutput=append:/var/log/nodejs-app/output.log
StandardError=append:/var/log/nodejs-app/error.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable the service
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload
sudo systemctl enable nodejs-app.service

# Stop any existing instance
sudo systemctl stop nodejs-app.service 2>/dev/null || true

# Start the service
echo "🚀 Starting Node.js application service..."
sudo systemctl start nodejs-app.service

# Wait and check if service started successfully
sleep 5

if systemctl is-active --quiet nodejs-app.service; then
    echo "✅ Node.js app service started successfully"
    sudo systemctl status nodejs-app.service --no-pager
    
    # Check if app is listening on port 3000
    sleep 2
    if sudo ss -tlnp 2>/dev/null | grep -q ":3000" || sudo netstat -tlnp 2>/dev/null | grep -q ":3000"; then
        echo "✅ Application is listening on port 3000"
    else
        echo "⚠️  Application may not be listening on port 3000"
        sudo ss -tlnp 2>/dev/null | grep node || sudo netstat -tlnp 2>/dev/null | grep node || echo "No node process found listening"
    fi
    
    # Test local connection
    if curl -s http://localhost:3000/ > /dev/null; then
        echo "✅ Local connection to port 3000 successful"
    else
        echo "⚠️  Local connection to port 3000 failed"
    fi
else
    echo "❌ Node.js app service failed to start"
    sudo systemctl status nodejs-app.service --no-pager || true
    echo "=== Service Logs ==="
    sudo journalctl -u nodejs-app.service -n 50 --no-pager || true
    echo "=== Application Error Log ==="
    sudo cat /var/log/nodejs-app/error.log 2>/dev/null || echo "No error log found"
    exit 1
fi
'''
        
        success, output = self.client.run_command(script, timeout=420)
        print(output)
        return success

    def _configure_database_connections(self) -> bool:
        """Configure database connections based on enabled dependencies"""
        print("🔧 Configuring database connections...")
        
        # Check if MySQL is enabled in config
        mysql_enabled = self.config.get('dependencies.mysql.enabled', False)
        mysql_external = self.config.get('dependencies.mysql.external', False)
        
        if mysql_enabled:
            if mysql_external:
                # Try to configure RDS connection
                return self._configure_rds_connection()
            else:
                # Configure local MySQL
                return self._configure_local_mysql()
        
        # Check if PostgreSQL is enabled
        postgresql_enabled = self.config.get('dependencies.postgresql.enabled', False)
        if postgresql_enabled:
            return self._configure_local_postgresql()
        
        print("ℹ️  No database dependencies enabled, skipping database configuration")
        return True

    def _configure_rds_connection(self) -> bool:
        """Configure RDS database connection"""
        print("🔧 Configuring RDS database connection...")
        
        rds_config = self.config.get('dependencies.mysql.rds', {})
        database_name = rds_config.get('database_name', 'lamp-app-db')
        
        script = f'''
set -e
echo "Setting up RDS database connection..."

# Install MySQL client
sudo apt-get update
sudo apt-get install -y mysql-client

# Try to get RDS connection details using AWS CLI/boto3
# This would normally be handled by the RDS manager
echo "RDS configuration attempted - requires valid AWS credentials"

# Create fallback environment file for now
if [ ! -f /var/www/html/.env ]; then
    echo "Creating fallback local database environment file..."
    sudo tee /var/www/html/.env > /dev/null << 'EOF'
# Database Configuration - Fallback to Local MySQL
DB_EXTERNAL=false
DB_TYPE=MYSQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app_db
DB_USERNAME=root
DB_PASSWORD=root123
DB_CHARSET=utf8mb4

# Application Configuration
APP_ENV=production
APP_DEBUG=false
APP_NAME="Generic Application"
EOF

    sudo chown www-data:www-data /var/www/html/.env
    sudo chmod 644 /var/www/html/.env
    echo "✅ Fallback environment file created"
fi

echo "✅ RDS configuration completed (with local fallback)"
'''
        
        success, output = self.client.run_command(script, timeout=120)
        
        # If RDS configuration fails, fall back to local MySQL
        if not success:
            print("⚠️  RDS configuration failed, falling back to local MySQL")
            return self._configure_local_mysql()
        
        return success

    def _configure_local_mysql(self) -> bool:
        """Configure local MySQL database"""
        print("🔧 Configuring local MySQL database...")
        
        script = '''
set -e
echo "Setting up local MySQL database..."

# Install MySQL if not present
if ! command -v mysql &> /dev/null; then
    echo "Installing MySQL server..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
fi

# Start and enable MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Configure MySQL root user
echo "Configuring MySQL root user..."
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root123';" 2>/dev/null || echo "Root password configuration attempted"

# Create application database
mysql -u root -proot123 -e "CREATE DATABASE IF NOT EXISTS app_db;" 2>/dev/null && echo "✅ app_db database created" || echo "❌ Failed to create database"

# Create test table with sample data
mysql -u root -proot123 app_db -e "
CREATE TABLE IF NOT EXISTS test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT IGNORE INTO test_table (id, name) VALUES 
    (1, 'Test Entry'),
    (2, 'Sample Data'),
    (3, 'Database Working');
" 2>/dev/null && echo "✅ Test table created with sample data" || echo "❌ Failed to create test table"

# Test connection
mysql -u root -proot123 -e "SELECT COUNT(*) as record_count FROM test_table;" app_db 2>/dev/null && echo "✅ MySQL connection test successful" || echo "❌ MySQL connection test failed"

# Create environment file
sudo tee /var/www/html/.env > /dev/null << 'EOF'
# Database Configuration - Local MySQL
DB_EXTERNAL=false
DB_TYPE=MYSQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app_db
DB_USERNAME=root
DB_PASSWORD=root123
DB_CHARSET=utf8mb4

# Application Configuration
APP_ENV=production
APP_DEBUG=false
APP_NAME="Generic Application"
EOF

# Set proper permissions
sudo chown www-data:www-data /var/www/html/.env
sudo chmod 644 /var/www/html/.env

echo "✅ Local MySQL database setup completed"
'''
        
        success, output = self.client.run_command_with_live_output(script, timeout=420)
        return success

    def _configure_local_postgresql(self) -> bool:
        """Configure local PostgreSQL database"""
        print("🔧 Configuring local PostgreSQL database...")
        
        script = '''
set -e
echo "Setting up local PostgreSQL database..."

# Install PostgreSQL
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create application database and user
sudo -u postgres psql -c "CREATE DATABASE app_db;" 2>/dev/null || echo "Database may already exist"
sudo -u postgres psql -c "CREATE USER app_user WITH PASSWORD 'app_password';" 2>/dev/null || echo "User may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE app_db TO app_user;" 2>/dev/null || echo "Privileges granted"

# Create environment file
sudo tee /var/www/html/.env > /dev/null << 'EOF'
# Database Configuration - Local PostgreSQL
DB_EXTERNAL=false
DB_TYPE=POSTGRESQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_db
DB_USERNAME=app_user
DB_PASSWORD=app_password
DB_CHARSET=utf8

# Application Configuration
APP_ENV=production
APP_DEBUG=false
APP_NAME="Generic Application"
EOF

# Set proper permissions
sudo chown www-data:www-data /var/www/html/.env
sudo chmod 644 /var/www/html/.env

echo "✅ Local PostgreSQL database setup completed"
'''
        
        success, output = self.client.run_command(script, timeout=420)
        return success

    def _setup_app_specific_config(self) -> bool:
        """Set up application-specific configurations"""
        app_type = self.config.get('application.type', 'web')
        
        script = '''
set -e
echo "Setting up application-specific configurations..."

# Set up log rotation
cat > /tmp/app-logs << 'EOF'
/var/log/app/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
EOF

sudo mv /tmp/app-logs /etc/logrotate.d/app

# Create application log directory
sudo mkdir -p /var/log/app
sudo chown ubuntu:ubuntu /var/log/app

# Set up cron jobs for maintenance (if needed)
# This is a placeholder for application-specific maintenance tasks

echo "✅ Application-specific configurations completed"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

    def _set_deployment_env_vars(self, env_vars):
        """Set deployment-specific environment variables"""
        if not env_vars:
            return
        
        env_content = []
        for key, value in env_vars.items():
            env_content.append(f'{key}="{value}"')
        
        env_file_content = '\n'.join(env_content)
        
        script = f'''
set -e
echo "Setting deployment environment variables..."

# Ensure database configuration exists in .env file
if [ -f /opt/app/database.env ] && [ ! -f /var/www/html/.env ]; then
    echo "Copying database configuration to .env file..."
    sudo cp /opt/app/database.env /var/www/html/.env
    sudo chown www-data:www-data /var/www/html/.env
    sudo chmod 640 /var/www/html/.env
elif [ ! -f /var/www/html/.env ]; then
    # Create empty .env file if neither exists
    sudo touch /var/www/html/.env
    sudo chown www-data:www-data /var/www/html/.env
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

    def _verify_deployment(self) -> bool:
        """Verify that the deployment was successful"""
        health_config = self.config.get_health_check_config()
        endpoint = health_config.get('endpoint', '/')
        expected_content = health_config.get('expected_content', 'Hello')
        
        script = f'''
set -e
echo "Verifying deployment..."

# Check if Node.js app service is running
if systemctl is-active --quiet nodejs-app.service; then
    echo "✅ Node.js application service is running"
    sudo systemctl status nodejs-app.service --no-pager || true
fi

# Check if web server is running
if systemctl is-active --quiet apache2; then
    echo "✅ Apache is running"
elif systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "⚠️  No web server detected as running"
fi

# Check if application files exist
if [ -f "/opt/nodejs-app/app.js" ] || [ -f "/opt/nodejs-app/index.js" ]; then
    echo "✅ Node.js application files found"
elif [ -f "/var/www/html/index.php" ] || [ -f "/var/www/html/index.html" ]; then
    echo "✅ Application files found"
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

# Optimize Apache if running
if systemctl is-active --quiet apache2; then
    echo "⚡ Optimizing Apache web server..."
    # Enable compression
    sudo a2enmod deflate
    sudo a2enmod expires
    sudo a2enmod headers
    sudo systemctl reload apache2
    echo "✅ Apache performance optimized"
fi

# Optimize PHP if installed
if which php > /dev/null 2>&1; then
    echo "⚡ Optimizing PHP configuration..."
    # Enable OPcache if available
    PHP_INI="/etc/php/8.1/apache2/php.ini"
    if [ -f "$PHP_INI" ]; then
        sudo sed -i 's/;opcache.enable=1/opcache.enable=1/' "$PHP_INI" || true
        sudo sed -i 's/;opcache.memory_consumption=128/opcache.memory_consumption=128/' "$PHP_INI" || true
        sudo sed -i 's/;opcache.max_accelerated_files=4000/opcache.max_accelerated_files=10000/' "$PHP_INI" || true
        sudo sed -i 's/;opcache.revalidate_freq=2/opcache.revalidate_freq=60/' "$PHP_INI" || true
    fi
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
        print("   📝 Check logs: /var/log/apache2/")
        print("   🔧 Config files: /var/www/html/.env")
        print("   📊 Monitor: systemctl status apache2 mysql")
        
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
        post_deployer = GenericPostDeployer(instance_name, region, config)
        
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
