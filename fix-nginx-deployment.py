#!/usr/bin/env python3
"""
Quick fix script for Nginx 403 permission issues
"""

import boto3
import sys
import argparse
import paramiko
import io
import base64
import time

def run_ssh_command(ssh, command, sudo=False):
    """Execute command via SSH"""
    if sudo:
        command = f"sudo {command}"
    
    print(f"  Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=60)
    
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    exit_code = stdout.channel.recv_exit_status()
    
    if output:
        print(f"  Output: {output.strip()}")
    if error and exit_code != 0:
        print(f"  Error: {error.strip()}")
    
    return exit_code == 0

def main():
    parser = argparse.ArgumentParser(description='Fix Nginx deployment permissions')
    parser.add_argument('--instance-name', default='nginx-static-demo', help='Instance name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    args = parser.parse_args()
    
    print("🔧 Nginx Deployment Fixer")
    print("=" * 60)
    
    # Initialize AWS client
    lightsail = boto3.client('lightsail', region_name=args.region)
    
    # Get instance info
    try:
        instance = lightsail.get_instance(instanceName=args.instance_name)['instance']
        ip = instance['publicIpAddress']
        
        print(f"✅ Instance: {args.instance_name}")
        print(f"✅ IP: {ip}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to get instance info: {e}")
        sys.exit(1)
    
    # Get SSH key
    try:
        key_response = lightsail.download_default_key_pair()
        private_key = key_response['privateKeyBase64']
        
        key_file = io.StringIO(base64.b64decode(private_key).decode('utf-8'))
        private_key_obj = paramiko.RSAKey.from_private_key(key_file)
        
    except Exception as e:
        print(f"❌ Failed to get SSH key: {e}")
        sys.exit(1)
    
    # Connect via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"🔌 Connecting to {ip}...")
        ssh.connect(ip, username='ubuntu', pkey=private_key_obj, timeout=30)
        print("✅ Connected!")
        print()
        
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        sys.exit(1)
    
    # Fix 1: Set correct ownership
    print("🔧 Fix 1: Setting correct file ownership...")
    run_ssh_command(ssh, "chown -R www-data:www-data /var/www/html/", sudo=True)
    print()
    
    # Fix 2: Set correct permissions
    print("🔧 Fix 2: Setting correct file permissions...")
    run_ssh_command(ssh, "chmod -R 755 /var/www/html/", sudo=True)
    run_ssh_command(ssh, "find /var/www/html -type f -name '*.html' -exec chmod 644 {} \\;", sudo=True)
    run_ssh_command(ssh, "find /var/www/html -type f -name '*.css' -exec chmod 644 {} \\;", sudo=True)
    run_ssh_command(ssh, "find /var/www/html -type f -name '*.js' -exec chmod 644 {} \\;", sudo=True)
    print()
    
    # Fix 3: Verify nginx config
    print("🔧 Fix 3: Verifying nginx configuration...")
    if run_ssh_command(ssh, "nginx -t", sudo=True):
        print("✅ Nginx config is valid")
    else:
        print("❌ Nginx config has errors")
    print()
    
    # Fix 4: Restart nginx
    print("🔧 Fix 4: Restarting nginx...")
    run_ssh_command(ssh, "systemctl restart nginx", sudo=True)
    time.sleep(2)
    
    if run_ssh_command(ssh, "systemctl is-active nginx", sudo=True):
        print("✅ Nginx is running")
    else:
        print("❌ Nginx failed to start")
    print()
    
    # Fix 5: Test locally
    print("🔧 Fix 5: Testing local access...")
    run_ssh_command(ssh, "curl -I http://localhost/", sudo=False)
    print()
    
    # Verify files
    print("📋 Verification: Listing web root...")
    run_ssh_command(ssh, "ls -la /var/www/html/", sudo=False)
    print()
    
    ssh.close()
    
    print("=" * 60)
    print("✅ Fixes applied!")
    print(f"🌐 Test your site: http://{ip}/")
    print()

if __name__ == '__main__':
    main()
