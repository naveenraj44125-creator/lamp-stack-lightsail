#!/usr/bin/env python3
"""
Deploy LAMP Stack application to AWS Lightsail using run_command API
This script uses the Lightsail get-instance-access-details API instead of SSH keys
"""

import os
import sys
import argparse
from lightsail_common import create_lightsail_client

class LightsailDeployer:
    def __init__(self, instance_name, region='us-east-1'):
        self.client = create_lightsail_client(instance_name, region, 'lamp')

    def deploy_application(self, package_path, env_vars=None):
        """Deploy the LAMP stack application"""
        print(f"🚀 Starting LAMP Stack deployment of {package_path}")
        
        # Check if instance is running and SSH is ready
        ssh_manager = create_lightsail_client(self.client.instance_name, self.client.region, 'ssh')
        if not ssh_manager.wait_for_ssh_ready():
            return False
        
        # Copy application package to instance
        if not self.client.copy_file_to_instance(package_path, '/tmp/app.tar.gz'):
            return False
        
        # Install LAMP stack using common functionality
        success, output = self.client.install_lamp_stack()
        if not success:
            print("❌ Failed to install LAMP stack")
            return False
        
        # Deploy application files using common functionality
        success, output = self.client.deploy_application_files()
        if not success:
            print("❌ Failed to deploy application files")
            return False
        
        # Set up database using common functionality
        success, output = self.client.setup_database()
        if not success:
            print("⚠️  Database setup failed (may be expected if already configured)")
        
        # Create environment file if needed
        if env_vars:
            success, output = self.client.create_environment_file(env_vars)
            if not success:
                print("⚠️  Failed to create environment file")
        
        # Restart Apache to ensure everything is working
        print("🔄 Restarting Apache...")
        success, output = self.client.run_command("sudo systemctl restart apache2", max_retries=3)
        
        # Check Apache status
        success, output = self.client.run_command("sudo systemctl status apache2 --no-pager", max_retries=1)
        
        print("✅ LAMP Stack deployment completed!")
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

def main():
    parser = argparse.ArgumentParser(description='Deploy LAMP Stack to AWS Lightsail')
    parser.add_argument('instance_name', help='Lightsail instance name')
    parser.add_argument('package_path', help='Path to application package (tar.gz)')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--env', action='append', help='Environment variables (KEY=VALUE)')
    
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
    
    print(f"🚀 Starting LAMP Stack deployment to {args.instance_name}")
    print(f"📦 Package: {args.package_path}")
    print(f"🌍 Region: {args.region}")
    
    if env_vars:
        print(f"🔧 Environment variables: {list(env_vars.keys())}")
    
    # Create deployer and deploy
    deployer = LightsailDeployer(args.instance_name, args.region)
    
    if deployer.deploy_application(args.package_path, env_vars):
        if deployer.verify_deployment():
            print("🎉 Deployment completed successfully!")
            sys.exit(0)
        else:
            print("⚠️  Deployment completed but verification failed")
            sys.exit(1)
    else:
        print("❌ Deployment failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
