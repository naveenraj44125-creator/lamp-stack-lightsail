#!/usr/bin/env python3
"""
Common post-deployment steps for AWS Lightsail deployments
This script handles general application deployment that applies to any deployment type
"""

import os
import sys
import argparse
from lightsail_common import create_lightsail_client

class LightsailCommonPostDeployer:
    def __init__(self, instance_name, region='us-east-1'):
        self.instance_name = instance_name
        self.region = region
        self.client = create_lightsail_client(instance_name, region, 'ssh')

    def upload_application_package(self, package_path):
        """Upload application package to the instance"""
        print(f"📦 Uploading application package: {package_path}")
        
        # Check if package exists locally
        if not os.path.exists(package_path):
            print(f"❌ Package file not found: {package_path}")
            return False
        
        # Copy application package to instance
        if not self.client.copy_file_to_instance(package_path, '/tmp/app.tar.gz'):
            print("❌ Failed to upload application package")
            return False
        
        print("✅ Application package uploaded successfully")
        return True

    def extract_application_files(self):
        """Extract application files from the uploaded package"""
        print("📂 Extracting application files...")
        
        extract_script = '''
set -e

# Create extraction directory
mkdir -p /tmp/app_extract
cd /tmp/app_extract

# Extract the application package
tar -xzf /tmp/app.tar.gz

# List extracted contents
echo "Extracted files:"
ls -la

echo "✅ Application files extracted successfully"
'''
        
        success, output = self.client.run_command(extract_script, timeout=60, max_retries=3)
        if not success:
            print("❌ Failed to extract application files")
            print(f"Error output: {output}")
            return False
        
        print("✅ Application files extracted successfully")
        return True

    def create_environment_file(self, env_vars=None):
        """Create environment configuration file"""
        if not env_vars:
            print("ℹ️  No environment variables provided, skipping environment file creation")
            return True
        
        print("🔧 Creating environment configuration file...")
        
        # Create environment file content
        env_content = "# Environment variables for application\n"
        for key, value in env_vars.items():
            env_content += f"{key}={value}\n"
        
        env_script = f'''
set -e

# Create environment file
cat > /tmp/app_extract/.env << 'EOF'
{env_content}
EOF

# Set proper permissions
chmod 644 /tmp/app_extract/.env

echo "✅ Environment file created"
'''
        
        success, output = self.client.run_command(env_script, timeout=30, max_retries=2)
        if not success:
            print("❌ Failed to create environment file")
            print(f"Error output: {output}")
            return False
        
        print("✅ Environment file created successfully")
        return True

    def verify_basic_deployment(self):
        """Perform basic deployment verification"""
        print("🔍 Performing basic deployment verification...")
        
        verify_script = '''
set -e

# Check if application files exist
if [ -d "/tmp/app_extract" ]; then
    echo "✅ Application extraction directory exists"
    ls -la /tmp/app_extract/ | head -10
else
    echo "❌ Application extraction directory not found"
    exit 1
fi

# Check disk space
echo "Disk space check:"
df -h /tmp

echo "✅ Basic deployment verification completed"
'''
        
        success, output = self.client.run_command(verify_script, timeout=30, max_retries=2)
        if not success:
            print("❌ Basic deployment verification failed")
            print(f"Error output: {output}")
            return False
        
        print("✅ Basic deployment verification completed")
        return True

    def cleanup_deployment_files(self):
        """Clean up temporary deployment files"""
        print("🧹 Cleaning up temporary deployment files...")
        
        cleanup_script = '''
set -e

# Clean up temporary files
rm -f /tmp/app.tar.gz
rm -rf /tmp/deployment/*

# Keep extracted files for the next step
echo "✅ Temporary deployment files cleaned up"
'''
        
        success, output = self.client.run_command(cleanup_script, timeout=60, max_retries=1)
        if not success:
            print("⚠️  Cleanup failed (non-critical)")
            print(f"Output: {output}")
        else:
            print("✅ Cleanup completed successfully")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Common post-deployment steps for AWS Lightsail')
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
    
    print(f"🚀 Starting common post-deployment steps for {args.instance_name}")
    print(f"📦 Package: {args.package_path}")
    print(f"🌍 Region: {args.region}")
    
    if env_vars:
        print(f"🔧 Environment variables: {list(env_vars.keys())}")
    
    # Create post-deployer
    post_deployer = LightsailCommonPostDeployer(args.instance_name, args.region)
    
    success = True
    
    # Upload application package
    if not post_deployer.upload_application_package(args.package_path):
        print("❌ Application package upload failed")
        success = False
    
    # Extract application files
    if success and not post_deployer.extract_application_files():
        print("❌ Application file extraction failed")
        success = False
    
    # Create environment file
    if success and not post_deployer.create_environment_file(env_vars):
        print("❌ Environment file creation failed")
        success = False
    
    # Verify deployment if requested
    if success and args.verify:
        if not post_deployer.verify_basic_deployment():
            print("⚠️  Basic deployment verification failed")
            success = False
    
    # Cleanup if requested
    if args.cleanup:
        post_deployer.cleanup_deployment_files()
    
    if success:
        print("🎉 Common post-deployment steps completed successfully!")
        sys.exit(0)
    else:
        print("❌ Common post-deployment steps failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
