#!/usr/bin/env python3
"""
LAMP-specific post-deployment steps for AWS Lightsail
This script handles LAMP stack application deployment and configuration
"""

import sys
import argparse
from lightsail_lamp import LightsailLAMPManager
from config_loader import ConfigLoader

class LightsailLAMPPostDeployer:
    def __init__(self, instance_name=None, region=None, config=None):
        # Initialize configuration
        if config is None:
            config = ConfigLoader()
        
        # Use config values if parameters not provided
        if instance_name is None:
            instance_name = config.get_instance_name()
        if region is None:
            region = config.get_aws_region()
            
        self.config = config
        self.client = LightsailLAMPManager(instance_name, region)

    def deploy_lamp_application(self):
        """Deploy application files to LAMP web directory"""
        print(f"🌐 Deploying LAMP application files...")
        
        # Deploy application files from the extracted directory
        deploy_script = '''
set -e

# Check if extracted files exist
if [ ! -d "/tmp/app_extract" ]; then
    echo "❌ Application extraction directory not found"
    exit 1
fi

# Backup current version if it exists
if [ -f "/var/www/html/index.html" ]; then
    echo "Backing up default Apache page..."
    sudo mv /var/www/html/index.html /var/www/html/index.html.backup.$(date +%Y%m%d_%H%M%S)
fi

# Deploy new version from extracted files
echo "Deploying application files to web directory..."
cd /tmp/app_extract
sudo cp -r * /var/www/html/
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

# Set specific permissions for PHP files
find /var/www/html -name "*.php" -exec sudo chmod 644 {} \\;

echo "✅ Application files deployed successfully"
'''
        
        success, output = self.client.run_command(deploy_script, timeout=300, max_retries=3)
        if not success:
            print("❌ Failed to deploy LAMP application files")
            print(f"Error output: {output}")
            return False
        
        print("✅ LAMP application files deployed successfully")
        return True

    def configure_lamp_services(self):
        """Configure LAMP services and permissions"""
        print("🔧 Configuring LAMP services and permissions...")
        
        configure_script = '''
set -e

# Set proper ownership and permissions for web directory
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

# Ensure PHP files have correct permissions
find /var/www/html -name "*.php" -exec sudo chmod 644 {} \\;

# Set special permissions for config directory if it exists
if [ -d "/var/www/html/config" ]; then
    sudo chmod 750 /var/www/html/config
    echo "✅ Config directory permissions set"
fi

# Ensure Apache is running and enabled
sudo systemctl enable apache2
sudo systemctl restart apache2

# Ensure MySQL is running and enabled
sudo systemctl enable mysql
sudo systemctl start mysql

# Check service status
echo "Apache status:"
sudo systemctl is-active apache2

echo "MySQL status:"
sudo systemctl is-active mysql

echo "✅ LAMP services configured successfully"
'''
        
        success, output = self.client.run_command(configure_script, timeout=120, max_retries=3)
        if not success:
            print("❌ Failed to configure LAMP services")
            print(f"Error output: {output}")
            return False
        
        print("✅ LAMP services configured successfully")
        return True

    def verify_lamp_deployment(self):
        """Verify LAMP deployment is working"""
        print("🔍 Verifying LAMP deployment...")
        
        try:
            # Get instance info
            instance_info = self.client.get_instance_info()
            if not instance_info:
                print("❌ Failed to get instance information")
                return False
            
            public_ip = instance_info['public_ip']
            print(f"🌐 Testing LAMP deployment at http://{public_ip}/")
            
            # Use LAMP-specific verification
            success, output = self.client.verify_lamp_stack()
            if not success:
                print("❌ LAMP stack verification failed")
                print(f"Error output: {output}")
                return False
            
            # Additional web server test
            web_test_script = '''
echo "Testing web server response..."

# Test local web server
curl -f -s http://localhost/ | head -20 || echo "Local web test failed"

# Check Apache configuration
sudo apache2ctl configtest

# Check PHP functionality
echo "<?php phpinfo(); ?>" | sudo tee /var/www/html/phpinfo.php > /dev/null
curl -f -s http://localhost/phpinfo.php | grep -i "PHP Version" || echo "PHP test completed"
sudo rm -f /var/www/html/phpinfo.php

echo "✅ Web server tests completed"
'''
            
            success, output = self.client.run_command(web_test_script, timeout=60, max_retries=2)
            if not success:
                print("⚠️  Some web server tests failed (may be non-critical)")
            
            print(f"✅ LAMP deployment verification completed")
            print(f"🌐 Application should be available at: http://{public_ip}/")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during LAMP verification: {e}")
            return False

    def optimize_lamp_performance(self):
        """Apply LAMP performance optimizations"""
        print("⚡ Applying LAMP performance optimizations...")
        
        optimize_script = '''
set -e

# Apache optimizations
echo "Applying Apache optimizations..."

# Enable mod_rewrite if not already enabled
sudo a2enmod rewrite || echo "mod_rewrite already enabled"

# Enable mod_deflate for compression
sudo a2enmod deflate || echo "mod_deflate already enabled"

# Enable mod_expires for caching
sudo a2enmod expires || echo "mod_expires already enabled"

# Restart Apache to apply changes
sudo systemctl restart apache2

# MySQL optimizations (basic)
echo "Checking MySQL configuration..."
sudo systemctl status mysql --no-pager | head -5

# PHP optimizations (basic)
echo "Checking PHP configuration..."
php -v | head -1

echo "✅ LAMP performance optimizations applied"
'''
        
        success, output = self.client.run_command(optimize_script, timeout=90, max_retries=2)
        if not success:
            print("⚠️  Some performance optimizations failed (non-critical)")
            print(f"Output: {output}")
        else:
            print("✅ LAMP performance optimizations completed")
        
        return True

    def finalize_lamp_deployment(self):
        """Finalize LAMP deployment with security and cleanup"""
        print("🔒 Finalizing LAMP deployment...")
        
        finalize_script = '''
set -e

# Remove extracted files from /tmp
rm -rf /tmp/app_extract

# Set secure permissions on sensitive files
if [ -f "/var/www/html/config/database.php" ]; then
    sudo chmod 640 /var/www/html/config/database.php
    echo "✅ Database config secured"
fi

# Remove any temporary PHP files
sudo find /var/www/html -name "*.tmp" -delete 2>/dev/null || true

# Final Apache restart
sudo systemctl restart apache2

# Log deployment completion
echo "$(date): LAMP deployment completed" | sudo tee -a /var/log/deployment.log

echo "✅ LAMP deployment finalized"
'''
        
        success, output = self.client.run_command(finalize_script, timeout=60, max_retries=2)
        if not success:
            print("⚠️  Some finalization steps failed (may be non-critical)")
            print(f"Output: {output}")
        else:
            print("✅ LAMP deployment finalized successfully")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='LAMP-specific post-deployment steps for AWS Lightsail')
    parser.add_argument('--instance-name', help='Lightsail instance name (overrides config)')
    parser.add_argument('--region', help='AWS region (overrides config)')
    parser.add_argument('--config-file', help='Path to configuration file')
    parser.add_argument('--verify', action='store_true', help='Verify LAMP deployment after completion')
    parser.add_argument('--optimize', action='store_true', help='Apply performance optimizations')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config_file = args.config_file if args.config_file else 'deployment.config.yml'
        config = ConfigLoader(config_file=config_file)
        
        # Use command line args if provided, otherwise use config
        instance_name = args.instance_name or config.get_instance_name()
        region = args.region or config.get_aws_region()
        
        print(f"🚀 Starting LAMP-specific post-deployment steps for {instance_name}")
        print(f"🌍 Region: {region}")
        
        # Check if LAMP steps are enabled in config
        if not config.get('deployment.steps.lamp.enabled', True):
            print("ℹ️  LAMP-specific steps are disabled in configuration")
            sys.exit(0)
        
        # Get configuration options
        verify_enabled = args.verify or config.get('deployment.steps.lamp.verify', True)
        optimize_enabled = args.optimize or config.get('deployment.steps.lamp.optimize', False)
        
        # Create LAMP post-deployer
        lamp_post_deployer = LightsailLAMPPostDeployer(instance_name, region, config)
        
        success = True
        
        # Deploy LAMP application
        if not lamp_post_deployer.deploy_lamp_application():
            print("❌ LAMP application deployment failed")
            success = False
        
        # Configure LAMP services
        if success and not lamp_post_deployer.configure_lamp_services():
            print("❌ LAMP services configuration failed")
            success = False
        
        # Apply optimizations if enabled
        if success and optimize_enabled:
            if not lamp_post_deployer.optimize_lamp_performance():
                print("⚠️  LAMP performance optimization failed (non-critical)")
        
        # Verify deployment if enabled
        if success and verify_enabled:
            if not lamp_post_deployer.verify_lamp_deployment():
                print("⚠️  LAMP deployment verification failed")
                success = False
        
        # Finalize deployment
        if success:
            if not lamp_post_deployer.finalize_lamp_deployment():
                print("⚠️  LAMP deployment finalization had issues (may be non-critical)")
        
        if success:
            print("🎉 LAMP-specific post-deployment steps completed successfully!")
            sys.exit(0)
        else:
            print("❌ LAMP-specific post-deployment steps failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error in LAMP post-deployment steps: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
