#!/usr/bin/env python3
"""
Common post-deployment steps for AWS Lightsail deployments
This script handles general application deployment that applies to any deployment type
"""

import os
import sys
import argparse
from lightsail_common import create_lightsail_client
from config_loader import load_deployment_config

class LightsailCommonPostDeployer:
    def __init__(self, instance_name=None, region=None, config=None):
        self.config = config or load_deployment_config()
        self.instance_name = instance_name or self.config.get_instance_name()
        self.region = region or self.config.get_aws_region()
        self.client = create_lightsail_client(self.instance_name, self.region, 'ssh')

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
        # Get environment variables from config if not provided
        if not env_vars:
            env_vars = self.config.get_environment_variables()
        
        if not env_vars:
            print("ℹ️  No environment variables configured, skipping environment file creation")
            return True
        
        # Check if this step is enabled
        step_config = self.config.get_step_config('post_deployment.common')
        if not step_config.get('create_env_file', True):
            print("ℹ️  Environment file creation is disabled in configuration")
            return True
        
        print("🔧 Creating environment configuration file...")
        
        # Create environment file content
        env_content = "# Environment variables for application\n"
        for key, value in env_vars.items():
            env_content += f"{key}={value}\n"
        
        # Get security configuration for file permissions
        security_config = self.config.get_security_config()
        config_file_perms = security_config.get('file_permissions', {}).get('config_files', '600')
        
        env_script = f'''
set -e

# Create environment file
cat > /tmp/app_extract/.env << 'EOF'
{env_content}
EOF

# Set proper permissions
chmod {config_file_perms} /tmp/app_extract/.env

echo "✅ Environment file created"
'''
        
        timeout = self.config.get_timeout('command_execution')
        max_retries = self.config.get_max_retries()
        
        success, output = self.client.run_command(env_script, timeout=timeout, max_retries=max_retries)
        if not success:
            print("❌ Failed to create environment file")
            print(f"Error output: {output}")
            return False
        
        print("✅ Environment file created successfully")
        return True

    def verify_basic_deployment(self):
        """Perform basic deployment verification"""
        # Check if verification is enabled
        step_config = self.config.get_step_config('post_deployment.common')
        if not step_config.get('verify_extraction', True):
            print("ℹ️  Basic deployment verification is disabled in configuration")
            return True
        
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
        
        timeout = self.config.get_timeout('command_execution')
        max_retries = self.config.get_max_retries()
        
        success, output = self.client.run_command(verify_script, timeout=timeout, max_retries=max_retries)
        if not success:
            print("❌ Basic deployment verification failed")
            print(f"Error output: {output}")
            return False
        
        print("✅ Basic deployment verification completed")
        return True

    def cleanup_deployment_files(self):
        """Clean up temporary deployment files"""
        # Check if cleanup is enabled
        step_config = self.config.get_step_config('post_deployment.common')
        if not step_config.get('cleanup_temp_files', True):
            print("ℹ️  Temporary file cleanup is disabled in configuration")
            return True
        
        print("🧹 Cleaning up temporary deployment files...")
        
        cleanup_script = '''
set -e

# Clean up temporary files
rm -f /tmp/app.tar.gz
rm -rf /tmp/deployment/*

# Keep extracted files for the next step
echo "✅ Temporary deployment files cleaned up"
'''
        
        timeout = self.config.get_timeout('command_execution')
        
        success, output = self.client.run_command(cleanup_script, timeout=timeout, max_retries=1)
        if not success:
            print("⚠️  Cleanup failed (non-critical)")
            print(f"Output: {output}")
        else:
            print("✅ Cleanup completed successfully")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Common post-deployment steps for AWS Lightsail')
    parser.add_argument('package_path', help='Path to application package (tar.gz)')
    parser.add_argument('--instance-name', help='Lightsail instance name (overrides config)')
    parser.add_argument('--region', help='AWS region (overrides config)')
    parser.add_argument('--config', default='deployment.config.yml', help='Configuration file path')
    parser.add_argument('--env', action='append', help='Environment variables (KEY=VALUE) - overrides config')
    parser.add_argument('--verify', action='store_true', help='Force verification (overrides config)')
    parser.add_argument('--cleanup', action='store_true', help='Force cleanup (overrides config)')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_deployment_config(args.config)
        config.print_config_summary()
        
        # Parse environment variables from command line
        env_vars = {}
        if args.env:
            for env_var in args.env:
                if '=' in env_var:
                    key, value = env_var.split('=', 1)
                    env_vars[key] = value
        
        # Create post-deployer
        post_deployer = LightsailCommonPostDeployer(
            instance_name=args.instance_name,
            region=args.region,
            config=config
        )
        
        print(f"🚀 Starting common post-deployment steps for {post_deployer.instance_name}")
        print(f"📦 Package: {args.package_path}")
        print(f"🌍 Region: {post_deployer.region}")
        
        # Show environment variables (from config or command line)
        final_env_vars = env_vars if env_vars else config.get_environment_variables()
        if final_env_vars:
            print(f"🔧 Environment variables: {list(final_env_vars.keys())}")
        
        success = True
        
        # Check if post-deployment common steps are enabled
        if not config.is_step_enabled('post_deployment.common'):
            print("ℹ️  Common post-deployment steps are disabled in configuration")
            sys.exit(0)
        
        # Upload application package
        if not post_deployer.upload_application_package(args.package_path):
            print("❌ Application package upload failed")
            success = False
        
        # Extract application files
        if success and not post_deployer.extract_application_files():
            print("❌ Application file extraction failed")
            success = False
        
        # Create environment file
        if success and not post_deployer.create_environment_file(env_vars if env_vars else None):
            print("❌ Environment file creation failed")
            success = False
        
        # Verify deployment (from config or command line flag)
        step_config = config.get_step_config('post_deployment.common')
        should_verify = args.verify or step_config.get('verify_extraction', True)
        if success and should_verify:
            if not post_deployer.verify_basic_deployment():
                print("⚠️  Basic deployment verification failed")
                success = False
        
        # Cleanup (from config or command line flag)
        should_cleanup = args.cleanup or step_config.get('cleanup_temp_files', True)
        if should_cleanup:
            post_deployer.cleanup_deployment_files()
        
        if success:
            print("🎉 Common post-deployment steps completed successfully!")
            sys.exit(0)
        else:
            print("❌ Common post-deployment steps failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Configuration or initialization error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
