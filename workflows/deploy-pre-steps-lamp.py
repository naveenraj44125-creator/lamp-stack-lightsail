#!/usr/bin/env python3
"""
LAMP-specific pre-deployment steps for AWS Lightsail
This script handles LAMP stack installation and configuration
"""

import sys
import argparse
from lightsail_lamp import LightsailLAMPManager

class LightsailLAMPPreDeployer:
    def __init__(self, instance_name, region='us-east-1'):
        self.client = LightsailLAMPManager(instance_name, region)

    def prepare_lamp_environment(self):
        """Prepare LAMP-specific environment"""
        print(f"🔧 Preparing LAMP Stack environment")
        
        # Install LAMP stack components
        print("📦 Installing LAMP stack components...")
        success, output = self.client.install_lamp_stack()
        if not success:
            print("❌ Failed to install LAMP stack")
            print(f"Error output: {output}")
            return False
        
        print("✅ LAMP stack installation completed")
        
        # Set up database
        print("🗄️ Setting up database...")
        success, output = self.client.setup_database()
        if not success:
            print("⚠️  Database setup failed (may be expected if already configured)")
            print(f"Output: {output}")
        else:
            print("✅ Database setup completed")
        
        # Prepare web directory for LAMP deployment
        print("🌐 Preparing web directory...")
        web_prep_script = '''
set -e

# Backup current version if it exists
if [ -f "/var/www/html/index.html" ]; then
    echo "Backing up default Apache page..."
    sudo mv /var/www/html/index.html /var/www/html/index.html.backup.$(date +%Y%m%d_%H%M%S)
fi

# Set proper permissions for web directory
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

# Ensure Apache is running
sudo systemctl enable apache2
sudo systemctl start apache2

# Ensure MySQL is running
sudo systemctl enable mysql
sudo systemctl start mysql

echo "✅ LAMP environment preparation completed"
'''
        
        success, output = self.client.run_command(web_prep_script, timeout=60, max_retries=3)
        if not success:
            print("❌ Failed to prepare LAMP web environment")
            print(f"Error output: {output}")
            return False
        
        print("✅ LAMP-specific pre-deployment steps completed successfully!")
        return True

def main():
    parser = argparse.ArgumentParser(description='LAMP-specific pre-deployment steps for AWS Lightsail')
    parser.add_argument('instance_name', help='Lightsail instance name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    print(f"🔧 Starting LAMP-specific pre-deployment steps for {args.instance_name}")
    print(f"🌍 Region: {args.region}")
    
    # Create LAMP pre-deployer and prepare environment
    lamp_pre_deployer = LightsailLAMPPreDeployer(args.instance_name, args.region)
    
    if lamp_pre_deployer.prepare_lamp_environment():
        print("🎉 LAMP-specific pre-deployment steps completed successfully!")
        sys.exit(0)
    else:
        print("❌ LAMP-specific pre-deployment steps failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
