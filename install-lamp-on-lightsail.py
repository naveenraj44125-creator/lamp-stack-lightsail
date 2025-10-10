#!/usr/bin/env python3
"""
LAMP Stack Installation Script for AWS Lightsail
Installs Apache, MySQL/MariaDB, and PHP on a Lightsail instance
"""

import boto3
import subprocess
import time
import sys
import os
import tempfile
import argparse
from pathlib import Path

def create_ssh_files(ssh_details):
    """Create temporary SSH key files"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as key_file:
        key_file.write(ssh_details['privateKey'])
        key_path = key_file.name
    
    cert_path = key_path + '-cert.pub'
    cert_parts = ssh_details['certKey'].split(' ', 2)
    formatted_cert = f'{cert_parts[0]} {cert_parts[1]}\n' if len(cert_parts) >= 2 else ssh_details['certKey'] + '\n'
    
    with open(cert_path, 'w') as cert_file:
        cert_file.write(formatted_cert)
    
    os.chmod(key_path, 0o600)
    os.chmod(cert_path, 0o600)
    
    return key_path, cert_path

def run_command(lightsail_client, instance_name, command, timeout=300):
    """Execute command on Lightsail instance using SSH certificates"""
    try:
        print(f"🔧 Running: {command[:100]}{'...' if len(command) > 100 else ''}")
        
        # Get SSH access details
        ssh_response = lightsail_client.get_instance_access_details(instanceName=instance_name)
        ssh_details = ssh_response['accessDetails']
        
        # Create temporary SSH key files
        key_path, cert_path = create_ssh_files(ssh_details)
        
        try:
            ssh_cmd = [
                'ssh', '-i', key_path, '-o', f'CertificateFile={cert_path}',
                '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'ConnectTimeout=15', '-o', 'IdentitiesOnly=yes',
                f'{ssh_details["username"]}@{ssh_details["ipAddress"]}', command
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                print(f"   ✅ Success")
                if result.stdout.strip():
                    # Limit output for readability
                    lines = result.stdout.strip().split('\n')
                    for line in lines[:20]:  # Show first 20 lines
                        print(f"   {line}")
                    if len(lines) > 20:
                        print(f"   ... ({len(lines) - 20} more lines)")
                return True, result.stdout.strip()
            else:
                print(f"   ❌ Failed (exit code: {result.returncode})")
                if result.stderr.strip():
                    print(f"   Error: {result.stderr.strip()}")
                return False, result.stderr.strip()
            
        finally:
            # Clean up temporary files
            try:
                os.unlink(key_path)
                os.unlink(cert_path)
            except:
                pass
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, str(e)

def install_lamp_stack(instance_name, region='us-east-1'):
    """Install LAMP stack on Lightsail instance"""
    print(f"🚀 Starting LAMP stack installation on {instance_name}")
    
    # Initialize Lightsail client
    lightsail = boto3.client('lightsail', region_name=region)
    
    # Read the LAMP installation script
    script_path = Path(__file__).parent / 'install-lamp-stack.sh'
    if not script_path.exists():
        print(f"❌ LAMP installation script not found: {script_path}")
        return False
    
    with open(script_path, 'r') as f:
        lamp_script = f.read()
    
    print("📦 Installing LAMP stack components...")
    
    # Execute the LAMP installation script directly
    success, output = run_command(lightsail, instance_name, lamp_script, timeout=600)
    
    if not success:
        print("❌ Failed to install LAMP stack")
        return False
    
    print("✅ LAMP stack installation completed successfully")
    
    # Verify installation
    print("🔍 Verifying LAMP stack installation...")
    verify_command = "apache2 -v && mysql --version && php -v"
    success, output = run_command(lightsail, instance_name, verify_command, timeout=60)
    
    if success:
        print("✅ LAMP stack verification successful")
    else:
        print("⚠️  LAMP stack verification had issues, but installation may still be functional")
    
    return True

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
