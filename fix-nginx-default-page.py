#!/usr/bin/env python3
"""
Fix nginx default page issue for specific instances
"""

import boto3
import requests
import subprocess
import sys
import time
from typing import Optional

def get_instance_ip(instance_name: str) -> Optional[str]:
    """Get the public IP of a Lightsail instance"""
    try:
        client = boto3.client('lightsail', region_name='us-east-1')
        response = client.get_instance(instanceName=instance_name)
        return response['instance']['publicIpAddress']
    except Exception as e:
        print(f"❌ Error getting IP for {instance_name}: {str(e)}")
        return None

def test_for_nginx_default(url: str) -> bool:
    """Test if URL shows nginx default page"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text.lower()
            nginx_indicators = [
                "welcome to nginx",
                "nginx.*default", 
                "test page for the nginx",
                "nginx http server",
                "default nginx page"
            ]
            return any(indicator in content for indicator in nginx_indicators)
    except:
        pass
    return False

def fix_nginx_via_aws_ssm(instance_name: str) -> bool:
    """Fix nginx configuration using AWS Systems Manager"""
    try:
        ssm_client = boto3.client('ssm', region_name='us-east-1')
        
        # Command to fix nginx configuration
        command = """#!/bin/bash
set -e

echo "🔧 Fixing nginx configuration via SSM..."

# Backup original nginx.conf if not already backed up
if [ ! -f /etc/nginx/nginx.conf.original ]; then
    sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.original
    echo "✅ Backed up original nginx.conf"
fi

# Completely remove the default server block from nginx.conf
sudo python3 << 'PYTHON_EOF'
import re

# Read the original nginx.conf
with open('/etc/nginx/nginx.conf', 'r') as f:
    content = f.read()

# Find and completely remove the server block within the http context
lines = content.split('\\n')
new_lines = []
in_server_block = False
brace_count = 0

for line in lines:
    stripped = line.strip()
    
    # Check if we're starting a server block
    if 'server' in stripped and '{' in stripped and not in_server_block:
        # This is the start of a server block - skip it entirely
        in_server_block = True
        brace_count = stripped.count('{') - stripped.count('}')
        continue
    
    if in_server_block:
        # Count braces to know when server block ends
        brace_count += line.count('{') - line.count('}')
        
        # If brace_count reaches 0, we've closed the server block
        if brace_count <= 0:
            in_server_block = False
        continue
    
    # Keep all other lines
    new_lines.append(line)

# Write the new content without the server block
new_content = '\\n'.join(new_lines)
with open('/etc/nginx/nginx.conf', 'w') as f:
    f.write(new_content)

print("✅ Completely removed default server block from nginx.conf")
PYTHON_EOF

# Remove default files
sudo rm -f /etc/nginx/conf.d/default.conf
sudo rm -f /usr/share/nginx/html/index.html

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

echo "✅ Nginx configuration fixed and restarted"
"""
        
        # Send command to instance
        response = ssm_client.send_command(
            InstanceIds=[instance_name],
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': [command]},
            TimeoutSeconds=300
        )
        
        command_id = response['Command']['CommandId']
        
        # Wait for command to complete
        print(f"⏳ Waiting for SSM command to complete...")
        time.sleep(10)
        
        # Get command result
        result = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_name
        )
        
        if result['Status'] == 'Success':
            print("✅ Nginx fix applied successfully via SSM")
            return True
        else:
            print(f"❌ SSM command failed: {result.get('StandardErrorContent', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error using SSM: {str(e)}")
        return False

def main():
    # Test cases with known nginx default page issues
    test_cases = [
        {
            "name": "Nginx Static Demo",
            "url": "http://18.215.255.226/",
            "instance": "nginx-static-demo-v6"
        }
    ]
    
    print("🔍 Checking for nginx default page issues...")
    
    for case in test_cases:
        print(f"\n🧪 Testing {case['name']}...")
        print(f"URL: {case['url']}")
        
        if test_for_nginx_default(case['url']):
            print("⚠️  NGINX DEFAULT PAGE DETECTED!")
            print(f"🔧 Attempting to fix {case['instance']}...")
            
            if fix_nginx_via_aws_ssm(case['instance']):
                print("✅ Fix applied, waiting for nginx to restart...")
                time.sleep(15)
                
                # Re-test
                if not test_for_nginx_default(case['url']):
                    print("🎉 SUCCESS! Nginx default page issue resolved!")
                else:
                    print("❌ Issue persists after fix attempt")
            else:
                print("❌ Failed to apply fix")
        else:
            print("✅ No nginx default page detected")

if __name__ == '__main__':
    main()