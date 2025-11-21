#!/usr/bin/env python3
"""
Universal post-deployment steps for AWS Lightsail
Works with any Linux distribution and any default user
"""

import sys
import argparse
from lightsail_common import LightsailBase
from config_loader import DeploymentConfig
from dependency_manager import DependencyManager

class UniversalPostDeployer:
    def __init__(self, instance_name=None, region=None, config=None):
        if config is None:
            config = DeploymentConfig()
        
        if instance_name is None:
            instance_name = config.get_instance_name()
        if region is None:
            region = config.get_aws_region()
            
        self.config = config
        self.client = LightsailBase(instance_name, region)
        self.dependency_manager = DependencyManager(self.client, config)
        self.system_config = self._detect_system_config()

    def _detect_system_config(self):
        """Detect OS, user, package manager, and service manager"""
        print("🔍 Detecting system configuration...")
        
        detection_script = '''
#!/bin/sh
set -e

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "OS_NAME=$NAME"
    echo "OS_ID=$ID"
    echo "OS_VERSION=$VERSION_ID"
elif [ -f /etc/redhat-release ]; then
    echo "OS_NAME=Red Hat Enterprise Linux"
    echo "OS_ID=rhel"
    echo "OS_VERSION=$(cat /etc/redhat-release | grep -oP '\\d+\\.\\d+' || echo unknown)"
else
    echo "OS_NAME=$(uname -s)"
    echo "OS_ID=unknown"
    echo "OS_VERSION=$(uname -r)"
fi

# Detect default user
if id ubuntu >/dev/null 2>&1; then
    echo "DEFAULT_USER=ubuntu"
elif id ec2-user >/dev/null 2>&1; then
    echo "DEFAULT_USER=ec2-user"
elif id centos >/dev/null 2>&1; then
    echo "DEFAULT_USER=centos"
elif id admin >/dev/null 2>&1; then
    echo "DEFAULT_USER=admin"
elif id bitnami >/dev/null 2>&1; then
    echo "DEFAULT_USER=bitnami"
else
    echo "DEFAULT_USER=root"
fi

# Detect package manager
if command -v apt-get >/dev/null 2>&1; then
    echo "PKG_MANAGER=apt-get"
elif command -v yum >/dev/null 2>&1; then
    echo "PKG_MANAGER=yum"
elif command -v dnf >/dev/null 2>&1; then
    echo "PKG_MANAGER=dnf"
else
    echo "PKG_MANAGER=unknown"
fi

# Detect service manager
if command -v systemctl >/dev/null 2>&1; then
    echo "SERVICE_MANAGER=systemctl"
elif command -v service >/dev/null 2>&1; then
    echo "SERVICE_MANAGER=service"
else
    echo "SERVICE_MANAGER=unknown"
fi

# Detect web root
if [ -d /var/www/html ]; then
    echo "WEB_ROOT=/var/www/html"
elif [ -d /usr/share/nginx/html ]; then
    echo "WEB_ROOT=/usr/share/nginx/html"
else
    echo "WEB_ROOT=/var/www/html"
fi
'''
        
        success, output = self.client.run_command(detection_script, timeout=60)
        
        config = {}
        if success:
            for line in output.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
        
        print(f"✅ OS: {config.get('OS_NAME', 'Unknown')}")
        print(f"✅ User: {config.get('DEFAULT_USER', 'ubuntu')}")
        print(f"✅ Package Manager: {config.get('PKG_MANAGER', 'apt-get')}")
        
        return config

    def deploy_application(self, package_file):
        """Deploy application"""
        print(f"🚀 Deploying {package_file}")
        
        # Upload package
        success = self.client.upload_file(package_file, f"/tmp/{package_file}")
        if not success:
            return False
        
        # Deploy based on app type
        app_type = self.config.get('application.type', 'web')
        deploy_path = self.config.get('application.deploy_path', '/var/www/html')
        
        deploy_script = f'''
set -e
cd /tmp
tar -xzf {package_file}
sudo mkdir -p {deploy_path}
sudo cp -r * {deploy_path}/
sudo chown -R {self.system_config.get('DEFAULT_USER', 'ubuntu')}:{self.system_config.get('DEFAULT_USER', 'ubuntu')} {deploy_path}
sudo chmod -R 755 {deploy_path}
'''
        
        success, output = self.client.run_command(deploy_script, timeout=300)
        if success:
            print("✅ Application deployed")
            self.dependency_manager.restart_services()
        
        return success

def main():
    parser = argparse.ArgumentParser(description='Universal deployment')
    parser.add_argument('--instance-name', help='Instance name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--config-file', help='Config file')
    parser.add_argument('--package-file', required=True, help='Package file')
    
    args = parser.parse_args()
    
    try:
        config = DeploymentConfig(args.config_file) if args.config_file else DeploymentConfig()
        deployer = UniversalPostDeployer(args.instance_name, args.region, config)
        success = deployer.deploy_application(args.package_file)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
