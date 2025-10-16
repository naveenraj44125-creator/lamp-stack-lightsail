#!/usr/bin/env python3
"""
Common pre-deployment steps for AWS Lightsail deployments
This script handles general environment preparation that applies to any deployment type
"""

import sys
import argparse
from lightsail_common import create_lightsail_client

class LightsailCommonPreDeployer:
    def __init__(self, instance_name, region='us-east-1'):
        self.instance_name = instance_name
        self.region = region
        self.client = create_lightsail_client(instance_name, region, 'ssh')

    def prepare_common_environment(self):
        """Prepare common environment for any deployment"""
        print(f"🔧 Preparing common environment for deployment")
        
        # Check if instance is running and SSH is ready
        print("🔍 Checking SSH connectivity...")
        if not self.client.wait_for_ssh_ready():
            print("❌ SSH connection failed")
            return False
        
        print("✅ SSH connection established")
        
        # Prepare deployment directory
        print("📁 Preparing deployment directory...")
        prep_script = '''
set -e

# Create temporary deployment directory
sudo mkdir -p /tmp/deployment
sudo chown $(whoami):$(whoami) /tmp/deployment

# Create backup directory if it doesn't exist
sudo mkdir -p /var/backups/deployments
sudo chown $(whoami):$(whoami) /var/backups/deployments

# Update system packages (non-interactive)
echo "Updating system packages..."
sudo apt-get update -qq > /dev/null 2>&1 || echo "Package update completed with warnings"

echo "✅ Common environment preparation completed"
'''
        
        success, output = self.client.run_command(prep_script, timeout=120, max_retries=3)
        if not success:
            print("❌ Failed to prepare common environment")
            print(f"Error output: {output}")
            return False
        
        print("✅ Common pre-deployment steps completed successfully!")
        return True

def main():
    parser = argparse.ArgumentParser(description='Common pre-deployment steps for AWS Lightsail')
    parser.add_argument('instance_name', help='Lightsail instance name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    print(f"🔧 Starting common pre-deployment steps for {args.instance_name}")
    print(f"🌍 Region: {args.region}")
    
    # Create pre-deployer and prepare environment
    pre_deployer = LightsailCommonPreDeployer(args.instance_name, args.region)
    
    if pre_deployer.prepare_common_environment():
        print("🎉 Common pre-deployment steps completed successfully!")
        sys.exit(0)
    else:
        print("❌ Common pre-deployment steps failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
