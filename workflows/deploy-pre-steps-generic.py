#!/usr/bin/env python3
"""
Generic pre-deployment steps for AWS Lightsail
This script handles dependency installation and configuration based on config
"""

import sys
import argparse
from lightsail_common import LightsailBase
from config_loader import DeploymentConfig
from dependency_manager import DependencyManager

class GenericPreDeployer:
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

    def prepare_environment(self):
        """Prepare generic application environment"""
        print("="*60)
        print("🔧 PREPARING APPLICATION ENVIRONMENT")
        print("="*60)
        
        # Get application configuration
        app_name = self.config.get('application.name', 'Generic Application')
        app_version = self.config.get('application.version', '1.0.0')
        app_type = self.config.get('application.type', 'web')
        enabled_deps = self.dependency_manager.get_enabled_dependencies()
        
        print(f"📋 Application: {app_name} v{app_version}")
        print(f"🏷️  Type: {app_type}")
        print(f"🌍 Instance: {self.client.instance_name}")
        print(f"📍 Region: {self.client.region}")
        print(f"📦 Dependencies to Install: {len(enabled_deps)}")
        
        if enabled_deps:
            print("   Dependencies:")
            for i, dep in enumerate(enabled_deps, 1):
                print(f"   {i}. {dep}")
        else:
            print("   No dependencies configured")
        
        # Pre-flight health check
        print("\n" + "="*60)
        print("🏥 SYSTEM HEALTH CHECK")
        print("="*60)
        health_ok = self._system_health_check()
        if not health_ok:
            print("⚠️  System health check found issues, but continuing with deployment...")
        else:
            print("✅ System health check passed")
        
        # Install all enabled dependencies
        print("\n" + "="*60)
        print("🚀 INSTALLING DEPENDENCIES")
        print("="*60)
        success, installed, failed = self.dependency_manager.install_all_dependencies()
        
        if not success:
            print(f"⚠️  Some dependencies failed to install: {', '.join(failed)}")
            if len(failed) == len(enabled_deps):
                print("❌ All dependencies failed to install")
                return False
        
        # Configure installed services
        if installed:
            print(f"\n" + "="*60)
            print(f"🔧 CONFIGURING {len(installed)} INSTALLED SERVICES")
            print("="*60)
            config_success = self.dependency_manager.configure_services()
            if not config_success:
                print("⚠️  Some service configurations failed")
        
        # Prepare application directory structure
        print("\n" + "="*60)
        print("📁 PREPARING DIRECTORY STRUCTURE")
        print("="*60)
        success = self._prepare_app_directories()
        if not success:
            print("❌ Failed to prepare application directories")
            return False
        
        # Set up environment variables
        print("\n" + "="*60)
        print("🌍 SETTING UP ENVIRONMENT VARIABLES")
        print("="*60)
        success = self._setup_environment_variables()
        if not success:
            print("⚠️  Failed to set up some environment variables")
        
        print("\n" + "="*60)
        print("✅ PRE-DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Print installation summary
        summary = self.dependency_manager.get_installation_summary()
        print(f"\n📊 Installation Summary:")
        print(f"   ✅ Installed: {len(summary['installed'])} dependencies")
        print(f"   ❌ Failed: {len(summary['failed'])} dependencies")
        print(f"   📈 Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['installed']:
            print(f"   📦 Installed Dependencies: {', '.join(summary['installed'])}")
        if summary['failed']:
            print(f"   ⚠️  Failed Dependencies: {', '.join(summary['failed'])}")
        
        return True

    def _prepare_app_directories(self) -> bool:
        """Prepare application directory structure"""
        app_type = self.config.get('application.type', 'web')
        
        # Determine web root based on installed web server and app type
        web_root = "/var/www/html"
        if 'nginx' in self.dependency_manager.installed_dependencies:
            web_root = self.config.get('dependencies.nginx.config.document_root', '/var/www/html')
        elif 'apache' in self.dependency_manager.installed_dependencies:
            web_root = self.config.get('dependencies.apache.config.document_root', '/var/www/html')
        
        script = f'''
set -e
echo "Preparing application directories..."

# Create main application directory
sudo mkdir -p {web_root}
sudo mkdir -p {web_root}/tmp
sudo mkdir -p {web_root}/logs
sudo mkdir -p {web_root}/config

# Create backup directory
sudo mkdir -p /var/backups/app

# Set proper ownership based on application type
if [ "{app_type}" = "web" ]; then
    # Web applications need www-data ownership
    sudo chown -R www-data:www-data {web_root}
    sudo chmod -R 755 {web_root}
    sudo chmod -R 777 {web_root}/tmp
    sudo chmod -R 755 {web_root}/logs
else
    # Other application types use ubuntu user
    sudo chown -R ubuntu:ubuntu {web_root}
    sudo chmod -R 755 {web_root}
fi

# Create application-specific directories based on dependencies
'''
        
        # Add Python-specific directories
        if 'python' in self.dependency_manager.installed_dependencies:
            script += '''
# Python application directories
sudo mkdir -p /opt/app
sudo mkdir -p /var/log/app
if [ -d "/opt/python-venv/app" ]; then
    sudo chown -R www-data:www-data /opt/python-venv
fi
'''
        
        # Add Node.js-specific directories
        if 'nodejs' in self.dependency_manager.installed_dependencies:
            script += '''
# Node.js application directories
sudo mkdir -p /opt/nodejs-app
sudo mkdir -p /var/log/nodejs
sudo chown -R ubuntu:ubuntu /opt/nodejs-app
'''
        
        # Add database-specific directories
        if 'mysql' in self.dependency_manager.installed_dependencies:
            # Only create mysql directories if using local MySQL (not external RDS)
            mysql_config = self.config.get('dependencies', {}).get('mysql', {})
            if not mysql_config.get('external', False):
                script += '''
# MySQL backup directory
sudo mkdir -p /var/backups/mysql
sudo chown -R mysql:mysql /var/backups/mysql
'''
        
        if 'postgresql' in self.dependency_manager.installed_dependencies:
            # Only create postgres directories if using local PostgreSQL (not external RDS)
            pg_config = self.config.get('dependencies', {}).get('postgresql', {})
            if not pg_config.get('external', False):
                script += '''
# PostgreSQL backup directory
sudo mkdir -p /var/backups/postgresql
sudo chown -R postgres:postgres /var/backups/postgresql
'''
        
        script += '''
echo "✅ Application directories prepared"
'''
        
        success, output = self.client.run_command(script, timeout=120)
        return success

    def _system_health_check(self) -> bool:
        """Perform system health checks before deployment"""
        print("🔍 Checking system health...")
        
        health_script = '''
#!/bin/bash
set +e  # Don't exit on error, we want to check everything

echo "Checking disk space..."
df -h / | tail -1 | awk '{print "Disk usage: " $5 " used of " $2}'

echo ""
echo "Checking memory..."
free -h | grep Mem | awk '{print "Memory: " $3 " used of " $2}'

echo ""
echo "Checking dpkg state..."
if sudo dpkg --audit 2>&1 | grep -q "broken"; then
    echo "❌ dpkg is in broken state"
    echo "Attempting to fix..."
    sudo dpkg --configure -a
    sudo apt-get install -f -y
    echo "✅ dpkg fixed"
else
    echo "✅ dpkg is healthy"
fi

echo ""
echo "Checking apt locks..."
if sudo lsof /var/lib/dpkg/lock-frontend 2>/dev/null; then
    echo "⚠️  apt is locked by another process"
    echo "Waiting for lock to be released..."
    sleep 10
else
    echo "✅ No apt locks detected"
fi

echo ""
echo "Checking connectivity..."
if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    echo "✅ Internet connectivity OK"
else
    echo "⚠️  Internet connectivity issue"
fi

echo ""
echo "✅ Health check completed"
'''
        
        success, output = self.client.run_command(health_script, timeout=120)
        return success

    def _setup_environment_variables(self) -> bool:
        """Set up application environment variables"""
        env_vars = self.config.get_environment_variables()
        
        if not env_vars:
            print("ℹ️  No environment variables configured")
            return True
        
        # Create environment file content
        env_content = []
        for key, value in env_vars.items():
            env_content.append(f'{key}="{value}"')
        
        env_file_content = '\n'.join(env_content)
        
        script = f'''
set -e
echo "Setting up environment variables..."

# Create environment file
cat > /tmp/app.env << 'EOF'
{env_file_content}
EOF

# Move to appropriate location based on application type
sudo mv /tmp/app.env /var/www/html/.env
sudo chown www-data:www-data /var/www/html/.env
sudo chmod 600 /var/www/html/.env

# Also create system-wide environment file
sudo cp /var/www/html/.env /etc/environment.d/app.conf || true

echo "✅ Environment variables configured"
'''
        
        success, output = self.client.run_command(script, timeout=60)
        return success

def main():
    parser = argparse.ArgumentParser(description='Generic pre-deployment steps for AWS Lightsail')
    parser.add_argument('--instance-name', help='Lightsail instance name (overrides config)')
    parser.add_argument('--region', help='AWS region (overrides config)')
    parser.add_argument('--config-file', help='Path to configuration file')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config_file = args.config_file if args.config_file else 'deployment-generic.config.yml'
        config = DeploymentConfig(config_file=config_file)
        
        # Use command line args if provided, otherwise use config
        instance_name = args.instance_name or config.get_instance_name()
        region = args.region or config.get_aws_region()
        
        print(f"🔧 Starting generic pre-deployment steps for {instance_name}")
        print(f"🌍 Region: {region}")
        print(f"📋 Application: {config.get('application.name', 'Unknown')} v{config.get('application.version', '1.0.0')}")
        print(f"🏷️  Type: {config.get('application.type', 'web')}")
        
        # Check if dependency steps are enabled in config
        if not config.get('deployment.steps.pre_deployment.dependencies.enabled', True):
            print("ℹ️  Dependency installation steps are disabled in configuration")
            sys.exit(0)
        
        # Create generic pre-deployer and prepare environment
        pre_deployer = GenericPreDeployer(instance_name, region, config)
        
        if pre_deployer.prepare_environment():
            print("🎉 Generic pre-deployment steps completed successfully!")
            sys.exit(0)
        else:
            print("❌ Generic pre-deployment steps failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error in generic pre-deployment steps: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
