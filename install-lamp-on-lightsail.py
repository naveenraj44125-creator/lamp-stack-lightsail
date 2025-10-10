#!/usr/bin/env python3
"""
LAMP Stack Installation Script for AWS Lightsail
Installs Apache, MySQL/MariaDB, and PHP on a Lightsail instance
"""

import boto3
import time
import sys
import os
import tempfile
import argparse
from pathlib import Path

def get_instance_access_details(lightsail_client, instance_name):
    """Get SSH access details for the Lightsail instance"""
    try:
        response = lightsail_client.get_instance_access_details(instanceName=instance_name)
        return response
    except Exception as e:
        print(f"❌ Error getting instance access details: {e}")
        return None

def install_lamp_stack(instance_name, region='us-east-1'):
    """Install LAMP stack on Lightsail instance"""
    print(f"🚀 Starting LAMP stack installation on {instance_name}")
    
    # Initialize Lightsail client
    lightsail = boto3.client('lightsail', region_name=region)
    
    # Get instance access details
    print("📡 Getting instance access details...")
    access_details = get_instance_access_details(lightsail, instance_name)
    
    if not access_details:
        print("❌ Failed to get instance access details")
        return False
    
    # Extract connection details
    host_keys = access_details.get('hostKeys', [])
    username = access_details.get('username', 'ubuntu')
    private_key = access_details.get('privateKey', '')
    
    if not private_key:
        print("❌ No private key available for SSH connection")
        return False
    
    print(f"✅ Got access details for user: {username}")
    
    # Create temporary key file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as key_file:
        key_file.write(private_key)
        key_file_path = key_file.name
    
    try:
        # Set proper permissions on key file
        os.chmod(key_file_path, 0o600)
        
        # Get the IP address
        instance_info = lightsail.get_instance(instanceName=instance_name)
        public_ip = instance_info['instance']['publicIpAddress']
        
        print(f"🌐 Connecting to {public_ip} as {username}")
        
        # Read the LAMP installation script
        script_path = Path(__file__).parent / 'install-lamp-stack.sh'
        if not script_path.exists():
            print(f"❌ LAMP installation script not found: {script_path}")
            return False
        
        with open(script_path, 'r') as f:
            lamp_script = f.read()
        
        # Copy script to instance and execute
        print("📦 Installing LAMP stack components...")
        
        # Create script on remote instance
        script_command = f'''
cat > /tmp/install-lamp.sh << 'EOF'
{lamp_script}
EOF
chmod +x /tmp/install-lamp.sh
'''
        
        # Execute script copy command
        copy_cmd = f'ssh -i {key_file_path} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {username}@{public_ip} "{script_command}"'
        copy_result = os.system(copy_cmd)
        
        if copy_result != 0:
            print("❌ Failed to copy installation script to instance")
            return False
        
        print("✅ Installation script copied to instance")
        
        # Execute the installation script
        print("🔧 Executing LAMP stack installation...")
        install_cmd = f'ssh -i {key_file_path} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {username}@{public_ip} "sudo /tmp/install-lamp.sh"'
        install_result = os.system(install_cmd)
        
        if install_result != 0:
            print("❌ LAMP stack installation failed")
            return False
        
        print("✅ LAMP stack installation completed successfully")
        
        # Verify installation
        print("🔍 Verifying LAMP stack installation...")
        verify_cmd = f'ssh -i {key_file_path} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {username}@{public_ip} "apache2 -v && mysql --version && php -v"'
        verify_result = os.system(verify_cmd)
        
        if verify_result == 0:
            print("✅ LAMP stack verification successful")
        else:
            print("⚠️  LAMP stack verification had issues, but installation may still be functional")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during LAMP installation: {e}")
        return False
    
    finally:
        # Clean up temporary key file
        try:
            os.unlink(key_file_path)
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description='Install LAMP stack on AWS Lightsail instance')
    parser.add_argument('instance_name', help='Name of the Lightsail instance')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    
    args = parser.parse_args()
    
    success = install_lamp_stack(args.instance_name, args.region)
    
    if success:
        print(f"🎉 LAMP stack installation completed on {args.instance_name}")
        sys.exit(0)
    else:
        print(f"💥 LAMP stack installation failed on {args.instance_name}")
        sys.exit(1)

if __name__ == '__main__':
    main()
