#!/usr/bin/env python3
"""
Test SSH access to Lightsail instance using get-instance-access-details
"""

import boto3
import subprocess
import tempfile
import os
import sys

def test_ssh_access(instance_name, region='us-east-1'):
    """Test SSH access to Lightsail instance"""
    try:
        # Create Lightsail client
        lightsail = boto3.client('lightsail', region_name=region)
        
        print(f"🔍 Testing SSH access to instance: {instance_name}")
        
        # Get SSH access details
        print("📋 Getting SSH access details...")
        ssh_response = lightsail.get_instance_access_details(instanceName=instance_name)
        ssh_details = ssh_response['accessDetails']
        
        print(f"   Username: {ssh_details['username']}")
        print(f"   IP Address: {ssh_details['ipAddress']}")
        print(f"   Protocol: {ssh_details['protocol']}")
        
        # Create temporary SSH key files
        print("🔑 Creating temporary SSH key files...")
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
        
        try:
            # Test SSH connection
            print("🔌 Testing SSH connection...")
            ssh_cmd = [
                'ssh', '-i', key_path, '-o', f'CertificateFile={cert_path}',
                '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'ConnectTimeout=30', '-o', 'ServerAliveInterval=10',
                '-o', 'ServerAliveCountMax=3', '-o', 'IdentitiesOnly=yes',
                '-o', 'BatchMode=yes', '-o', 'LogLevel=ERROR',
                f'{ssh_details["username"]}@{ssh_details["ipAddress"]}',
                'echo "SSH connection successful!" && whoami && uname -a && uptime'
            ]
            
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ SSH connection successful!")
                print("📤 Command output:")
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")
                return True
            else:
                print(f"❌ SSH connection failed (exit code: {result.returncode})")
                if result.stderr.strip():
                    print(f"   Error: {result.stderr.strip()}")
                return False
                
        finally:
            # Clean up temporary files
            try:
                os.unlink(key_path)
                os.unlink(cert_path)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    if len(sys.argv) > 1:
        instance_name = sys.argv[1]
    else:
        instance_name = "lamp-stack-demo"
    
    region = sys.argv[2] if len(sys.argv) > 2 else "us-east-1"
    
    print("🧪 SSH Access Test")
    print("=" * 50)
    print(f"Instance: {instance_name}")
    print(f"Region: {region}")
    print("=" * 50)
    
    success = test_ssh_access(instance_name, region)
    
    if success:
        print("\n✅ SSH access test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ SSH access test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
