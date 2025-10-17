#!/usr/bin/env python3
"""
Common pre-deployment steps for AWS Lightsail deployments
This script handles general environment preparation that applies to any deployment type
"""

import sys
import argparse
from lightsail_common import create_lightsail_client
from config_loader import ConfigLoader

class LightsailCommonPreDeployer:
    def __init__(self, instance_name=None, region=None, config=None):
        self.config = config or ConfigLoader()
        self.instance_name = instance_name or self.config.get_instance_name()
        self.region = region or self.config.get_aws_region()
        self.client = create_lightsail_client(self.instance_name, self.region, 'ssh')

    def prepare_common_environment(self):
        """Prepare common environment for any deployment"""
        print(f"🔧 Preparing common environment for deployment")
        
        # Check if this step is enabled
        if not self.config.get('deployment.steps.common.enabled', True):
            print("ℹ️  Common pre-deployment steps are disabled in configuration")
            return True
        
        # Check if instance is running and SSH is ready
        print("🔍 Checking SSH connectivity...")
        ssh_timeout = self.config.get('deployment.timeouts.ssh_connection', 300)
        if not self.client.wait_for_ssh_ready(timeout=ssh_timeout):
            print("❌ SSH connection failed")
            return False
        
        print("✅ SSH connection established")
        
        # Prepare deployment directory
        print("📁 Preparing deployment directory...")
        
        # Get backup configuration
        backup_location = self.config.get('backup.backup_location', '/var/backups/deployments')
        
        prep_script = f'''
set -e

# Create temporary deployment directory
sudo mkdir -p /tmp/deployment
sudo chown $(whoami):$(whoami) /tmp/deployment

# Create backup directory if it doesn't exist
sudo mkdir -p {backup_location}
sudo chown $(whoami):$(whoami) {backup_location}
'''
        
        # Add package update if enabled
        if self.config.get('deployment.steps.common.update_packages', True):
            prep_script += '''
# Update system packages (non-interactive)
echo "Updating system packages..."
sudo apt-get update -qq > /dev/null 2>&1 || echo "Package update completed with warnings"
'''
        
        prep_script += '''
echo "✅ Common environment preparation completed"
'''
        
        timeout = self.config.get('deployment.timeouts.command_execution', 300)
        max_retries = self.config.get('deployment.max_retries', 3)
        
        success, output = self.client.run_command(prep_script, timeout=timeout, max_retries=max_retries)
        if not success:
            print("❌ Failed to prepare common environment")
            print(f"Error output: {output}")
            return False
        
        print("✅ Common pre-deployment steps completed successfully!")
        return True

def main():
    parser = argparse.ArgumentParser(description='Common pre-deployment steps for AWS Lightsail')
    parser.add_argument('--instance-name', help='Lightsail instance name (overrides config)')
    parser.add_argument('--region', help='AWS region (overrides config)')
    parser.add_argument('--config', default='deployment.config.yml', help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = ConfigLoader(config_file=args.config)
        
        # Create pre-deployer and prepare environment
        pre_deployer = LightsailCommonPreDeployer(
            instance_name=args.instance_name,
            region=args.region,
            config=config
        )
        
        print(f"🔧 Starting common pre-deployment steps for {pre_deployer.instance_name}")
        print(f"🌍 Region: {pre_deployer.region}")
        
        if pre_deployer.prepare_common_environment():
            print("🎉 Common pre-deployment steps completed successfully!")
            sys.exit(0)
        else:
            print("❌ Common pre-deployment steps failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Configuration or initialization error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
