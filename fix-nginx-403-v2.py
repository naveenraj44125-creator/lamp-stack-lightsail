#!/usr/bin/env python3
"""Fix Nginx 403 permissions on Lightsail instance"""

import subprocess
import sys
import boto3
import os

# Load AWS credentials from file
if os.path.exists('.aws-creds.sh'):
    with open('.aws-creds.sh', 'r') as f:
        for line in f:
            if line.startswith('export '):
                key_value = line.replace('export ', '').strip()
                if '=' in key_value:
                    key, value = key_value.split('=', 1)
                    os.environ[key] = value

INSTANCE_NAME = "nginx-static-demo"
REGION = "us-east-1"

def run_ssh_command(ip, command, description):
    """Run SSH command and print output"""
    print(f"\n🔧 {description}")
    ssh_cmd = f'ssh -o StrictHostKeyChecking=no ubuntu@{ip} "{command}"'
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Success")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ Failed (exit code: {result.returncode})")
        if result.stderr:
            print(f"Error: {result.stderr}")
    
    return result.returncode == 0

def get_instance_ip():
    """Get instance public IP"""
    lightsail = boto3.client('lightsail', region_name=REGION)
    response = lightsail.get_instance(instanceName=INSTANCE_NAME)
    return response['instance']['publicIpAddress']

def main():
    print("🔧 Nginx 403 Permission Fixer")
    print("="*60)
    
    # Get instance IP
    print("\n📡 Getting instance IP...")
    ip = get_instance_ip()
    print(f"✅ Instance IP: {ip}")
    
    # Test SSH connection
    print("\n🔐 Testing SSH connection...")
    if not run_ssh_command(ip, "echo 'SSH connection successful'", "SSH Test"):
        print("❌ Cannot establish SSH connection")
        sys.exit(1)
    
    # List current files and permissions
    print("\n📋 Current files in /var/www/html:")
    run_ssh_command(ip, "ls -la /var/www/html/ | head -15", "List files")
    
    # Fix ownership
    run_ssh_command(ip, "sudo chown -R www-data:www-data /var/www/html/", "Set ownership to www-data")
    
    # Fix directory permissions
    run_ssh_command(ip, "sudo find /var/www/html -type d -exec chmod 755 {} \\;", "Set directory permissions (755)")
    
    # Fix file permissions
    run_ssh_command(ip, "sudo find /var/www/html -type f -exec chmod 644 {} \\;", "Set file permissions (644)")
    
    # Verify permissions
    print("\n📋 Updated permissions:")
    run_ssh_command(ip, "ls -la /var/www/html/ | head -15", "Verify permissions")
    
    # Test Nginx config
    run_ssh_command(ip, "sudo nginx -t", "Test Nginx configuration")
    
    # Restart Nginx
    run_ssh_command(ip, "sudo systemctl restart nginx", "Restart Nginx")
    
    # Check Nginx status
    run_ssh_command(ip, "sudo systemctl status nginx --no-pager | head -10", "Check Nginx status")
    
    # Test local access
    print("\n🧪 Testing local access...")
    run_ssh_command(ip, "curl -I http://localhost/", "Local HTTP test")
    
    print("\n✅ Fix complete!")
    print(f"🌐 Test at: http://{ip}/")

if __name__ == "__main__":
    main()
