#!/usr/bin/env python3
"""
Debug script for Nginx deployment issues
Checks file permissions, nginx config, and service status
"""

import boto3
import sys
import time
import argparse

def run_ssh_command(lightsail, instance_name, command, timeout=60):
    """Execute command via SSH on Lightsail instance"""
    try:
        response = lightsail.send_ssh_public_key(
            instanceName=instance_name,
            sshPublicKey='temp-key-for-command'
        )
        
        # Use AWS Systems Manager or direct SSH
        import paramiko
        
        # Get instance details
        instance = lightsail.get_instance(instanceName=instance_name)['instance']
        ip = instance['publicIpAddress']
        
        # Download SSH key
        key_response = lightsail.download_default_key_pair()
        private_key = key_response['privateKeyBase64']
        
        # Connect via SSH
        import io
        import base64
        
        key_file = io.StringIO(base64.b64decode(private_key).decode('utf-8'))
        private_key_obj = paramiko.RSAKey.from_private_key(key_file)
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {ip}...")
        ssh.connect(ip, username='ubuntu', pkey=private_key_obj, timeout=timeout)
        
        print(f"Executing: {command}")
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        exit_code = stdout.channel.recv_exit_status()
        
        ssh.close()
        
        return {
            'output': output,
            'error': error,
            'exit_code': exit_code
        }
        
    except Exception as e:
        print(f"Error executing command: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Debug Nginx deployment')
    parser.add_argument('--instance-name', default='nginx-static-demo', help='Instance name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    args = parser.parse_args()
    
    print("🔍 Nginx Deployment Debugger")
    print("=" * 60)
    
    # Initialize AWS client
    lightsail = boto3.client('lightsail', region_name=args.region)
    
    # Get instance info
    try:
        instance = lightsail.get_instance(instanceName=args.instance_name)['instance']
        ip = instance['publicIpAddress']
        state = instance['state']['name']
        
        print(f"✅ Instance: {args.instance_name}")
        print(f"✅ IP: {ip}")
        print(f"✅ State: {state}")
        print()
        
    except Exception as e:
        print(f"❌ Failed to get instance info: {e}")
        sys.exit(1)
    
    # Check 1: Nginx service status
    print("📋 Check 1: Nginx Service Status")
    print("-" * 60)
    result = run_ssh_command(lightsail, args.instance_name, "sudo systemctl status nginx")
    if result:
        print(result['output'])
        if result['error']:
            print(f"Error: {result['error']}")
    print()
    
    # Check 2: Nginx configuration test
    print("📋 Check 2: Nginx Configuration Test")
    print("-" * 60)
    result = run_ssh_command(lightsail, args.instance_name, "sudo nginx -t")
    if result:
        print(result['output'])
        if result['error']:
            print(result['error'])
    print()
    
    # Check 3: Web root directory
    print("📋 Check 3: Web Root Directory")
    print("-" * 60)
    result = run_ssh_command(lightsail, args.instance_name, "ls -la /var/www/html/")
    if result:
        print(result['output'])
    print()
    
    # Check 4: File permissions
    print("📋 Check 4: File Permissions")
    print("-" * 60)
    result = run_ssh_command(lightsail, args.instance_name, 
                            "stat -c '%a %U:%G %n' /var/www/html/* 2>/dev/null || echo 'No files found'")
    if result:
        print(result['output'])
    print()
    
    # Check 5: Nginx error log
    print("📋 Check 5: Nginx Error Log (last 20 lines)")
    print("-" * 60)
    result = run_ssh_command(lightsail, args.instance_name, 
                            "sudo tail -20 /var/log/nginx/error.log")
    if result:
        print(result['output'])
    print()
    
    # Check 6: Nginx access log
    print("📋 Check 6: Nginx Access Log (last 10 lines)")
    print("-" * 60)
    result = run_ssh_command(lightsail, args.instance_name, 
                            "sudo tail -10 /var/log/nginx/access.log")
    if result:
        print(result['output'])
    print()
    
    # Check 7: Nginx default site config
    print("📋 Check 7: Nginx Default Site Config")
    print("-" * 60)
    result = run_ssh_command(lightsail, args.instance_name, 
                            "cat /etc/nginx/sites-enabled/default")
    if result:
        print(result['output'])
    print()
    
    # Check 8: Test local curl
    print("📋 Check 8: Local Curl Test")
    print("-" * 60)
    result = run_ssh_command(lightsail, args.instance_name, 
                            "curl -I http://localhost/")
    if result:
        print(result['output'])
        if result['error']:
            print(result['error'])
    print()
    
    # Check 9: Check if index.html exists and is readable
    print("📋 Check 9: Index File Check")
    print("-" * 60)
    result = run_ssh_command(lightsail, args.instance_name, 
                            "test -f /var/www/html/index.html && echo 'File exists' || echo 'File missing'")
    if result:
        print(result['output'])
    
    result = run_ssh_command(lightsail, args.instance_name, 
                            "test -r /var/www/html/index.html && echo 'File readable' || echo 'File not readable'")
    if result:
        print(result['output'])
    print()
    
    # Suggested fixes
    print("🔧 Suggested Fixes")
    print("=" * 60)
    print("1. Fix file permissions:")
    print("   sudo chown -R www-data:www-data /var/www/html/")
    print("   sudo chmod -R 755 /var/www/html/")
    print("   sudo chmod 644 /var/www/html/*.html")
    print()
    print("2. Restart nginx:")
    print("   sudo systemctl restart nginx")
    print()
    print("3. Check nginx config:")
    print("   sudo nginx -t")
    print()

if __name__ == '__main__':
    main()
