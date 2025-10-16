#!/usr/bin/env python3
"""
Pre-deployment steps for LAMP Stack application to AWS Lightsail
This script handles environment preparation before application deployment
"""

import sys
import argparse
from lightsail_common import create_lightsail_client

class LightsailPreDeployer:
    def __init__(self, instance_name, region='us-east-1'):
        self.client = create_lightsail_client(instance_name, region, 'lamp')

    def prepare_environment(self):
        """Prepare the environment for LAMP stack deployment"""
        print(f"🔧 Preparing environment for LAMP Stack deployment")
        
        # Check if instance is running and SSH is ready
        ssh_manager = create_lightsail_client(self.client.instance_name, self.client.region, 'ssh')
        if not ssh_manager.wait_for_ssh_ready():
            return False
        
        # Install LAMP stack components using common functionality
        success, output = self.client.install_lamp_stack()
        if not success:
            print("❌ Failed to install LAMP stack")
            return False
        
        # Set up database using common functionality
        success, output = self.client.setup_database()
        if not success:
            print("⚠️  Database setup failed (may be expected if already configured)")
        
        # Prepare deployment directory
        print("📁 Preparing deployment directory...")
        prep_script = '''
set -e

# Create temporary deployment directory
sudo mkdir -p /tmp/deployment
sudo chown $(whoami):$(whoami) /tmp/deployment

# Backup current version if it exists
if [ -f "/var/www/html/index.html" ]; then
    echo "Backing up default Apache page..."
    sudo mv /var/www/html/index.html /var/www/html/index.html.backup.$(date +%Y%m%d_%H%M%S)
fi

echo "✅ Environment preparation completed"
'''
        
        success, output = self.client.run_command(prep_script, timeout=60, max_retries=3)
        if not success:
            print("❌ Failed to prepare deployment directory")
            return False
        
        print("✅ Pre-deployment steps completed successfully!")
        return True

def main():
    parser = argparse.ArgumentParser(description='Pre-deployment steps for LAMP Stack on AWS Lightsail')
    parser.add_argument('instance_name', help='Lightsail instance name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    print(f"🔧 Starting pre-deployment steps for {args.instance_name}")
    print(f"🌍 Region: {args.region}")
    
    # Create pre-deployer and prepare environment
    pre_deployer = LightsailPreDeployer(args.instance_name, args.region)
    
    if pre_deployer.prepare_environment():
        print("🎉 Pre-deployment steps completed successfully!")
        sys.exit(0)
    else:
        print("❌ Pre-deployment steps failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
