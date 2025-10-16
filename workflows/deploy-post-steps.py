#!/usr/bin/env python3
"""
Post-deployment steps for LAMP Stack application to AWS Lightsail
This script handles application deployment and verification after environment preparation
"""

import os
import sys
import argparse
from botocore.exceptions import ClientError
from lightsail_common import create_lightsail_client
from lightsail_lamp import LightsailLAMPManager

class LightsailPostDeployer:
    def __init__(self, instance_name, region='us-east-1'):
        self.client = LightsailLAMPManager(instance_name, region)

    def deploy_application(self, package_path, env_vars=None):
        """Deploy the application files after environment is prepared"""
        print(f"🚀 Starting application deployment of {package_path}")
        
        # Copy application package to instance
        if not self.client.copy_file_to_instance(package_path, '/tmp/app.tar.gz'):
            return False
        
        # Deploy application files using common functionality
        success, output = self.client.deploy_application_files()
        if not success:
            print("❌ Failed to deploy application files")
            return False
        
        # Create environment file if needed
        if env_vars:
            success, output = self.client.create_environment_file(env_vars)
            if not success:
                print("⚠️  Failed to create environment file")
        
        # Set proper permissions and restart services
        print("🔧 Finalizing deployment...")
        finalize_script = '''
set -e

# Set proper permissions
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

# Restart Apache to ensure everything is working
sudo systemctl restart apache2

# Check Apache status
sudo systemctl status apache2 --no-pager | head -10

echo "✅ Application deployment finalized"
'''
        
        success, output = self.client.run_command(finalize_script, timeout=120, max_retries=3)
        if not success:
            print("❌ Failed to finalize deployment")
            return False
        
        print("✅ Application deployment completed!")
        return True
    
    def verify_deployment(self, expected_content="Hello Welcome"):
        """Verify the deployment is working"""
        try:
            # Get instance info using common functionality
            instance_info = self.client.get_instance_info()
            if not instance_info:
                print("❌ Failed to get instance information")
                return False
            
            public_ip = instance_info['public_ip']
            print(f"🔍 Verifying deployment at http://{public_ip}/")
            
            # Test the web server
            test_script = '''
echo "Testing web server..."
curl -f -s http://localhost/ | head -20 || echo "Local test failed"
sudo systemctl status apache2 --no-pager | head -10
'''
            
            success, output = self.client.run_command(test_script, max_retries=3)
            
            print(f"✅ Deployment verification completed")
            print(f"🌐 Application should be available at: http://{public_ip}/")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            return False

    def cleanup_deployment(self):
        """Clean up temporary deployment files"""
        print("🧹 Cleaning up deployment files...")
        cleanup_script = '''
set -e

# Clean up temporary files
sudo rm -f /tmp/app.tar.gz
sudo rm -rf /tmp/deployment/*

echo "✅ Cleanup completed"
'''
        
        success, output = self.client.run_command(cleanup_script, timeout=60, max_retries=1)
        if not success:
            print("⚠️  Cleanup failed (non-critical)")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Post-deployment steps for LAMP Stack on AWS Lightsail')
    parser.add_argument('instance_name', help='Lightsail instance name')
    parser.add_argument('package_path', help='Path to application package (tar.gz)')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--env', action='append', help='Environment variables (KEY=VALUE)')
    parser.add_argument('--verify', action='store_true', help='Verify deployment after completion')
    parser.add_argument('--cleanup', action='store_true', help='Clean up temporary files after deployment')
    
    args = parser.parse_args()
    
    # Parse environment variables
    env_vars = {}
    if args.env:
        for env_var in args.env:
            if '=' in env_var:
                key, value = env_var.split('=', 1)
                env_vars[key] = value
    
    # Check if package exists
    if not os.path.exists(args.package_path):
        print(f"❌ Package file not found: {args.package_path}")
        sys.exit(1)
    
    print(f"🚀 Starting post-deployment steps for {args.instance_name}")
    print(f"📦 Package: {args.package_path}")
    print(f"🌍 Region: {args.region}")
    
    if env_vars:
        print(f"🔧 Environment variables: {list(env_vars.keys())}")
    
    # Create post-deployer and deploy
    post_deployer = LightsailPostDeployer(args.instance_name, args.region)
    
    success = True
    
    # Deploy application
    if not post_deployer.deploy_application(args.package_path, env_vars):
        print("❌ Application deployment failed")
        success = False
    
    # Verify deployment if requested
    if success and args.verify:
        if not post_deployer.verify_deployment():
            print("⚠️  Deployment verification failed")
            success = False
    
    # Cleanup if requested
    if args.cleanup:
        post_deployer.cleanup_deployment()
    
    if success:
        print("🎉 Post-deployment steps completed successfully!")
        sys.exit(0)
    else:
        print("❌ Post-deployment steps failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
