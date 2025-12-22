#!/usr/bin/env python3

import boto3
import subprocess
import sys
import os

def run_remote_command(instance_ip, command):
    """Run command on remote instance using AWS Session Manager or direct SSH"""
    
    # Try to find the instance ID from IP
    ec2 = boto3.client('ec2', region_name='us-east-1')
    
    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'ip-address', 'Values': [instance_ip]},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )
        
        instance_id = None
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                break
        
        if not instance_id:
            print(f"❌ Could not find instance ID for IP {instance_ip}")
            return None
            
        print(f"📡 Found instance {instance_id} for IP {instance_ip}")
        
        # Use AWS SSM to run the command
        ssm = boto3.client('ssm', region_name='us-east-1')
        
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': [command]},
            TimeoutSeconds=60
        )
        
        command_id = response['Command']['CommandId']
        
        # Wait for command to complete
        import time
        for i in range(30):  # Wait up to 30 seconds
            try:
                result = ssm.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=instance_id
                )
                
                if result['Status'] in ['Success', 'Failed']:
                    return {
                        'stdout': result.get('StandardOutputContent', ''),
                        'stderr': result.get('StandardErrorContent', ''),
                        'status': result['Status']
                    }
                    
            except ssm.exceptions.InvocationDoesNotExist:
                pass
                
            time.sleep(1)
            
        print(f"❌ Command timed out")
        return None
        
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return None

def check_nginx_config(instance_ip, instance_name):
    print(f'=== CHECKING {instance_name} ({instance_ip}) ===')
    
    command = '''
echo "📋 Checking nginx configuration directories:"
ls -la /etc/nginx/conf.d/ 2>/dev/null || echo "No conf.d directory"
echo ""
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "No sites-enabled directory"
echo ""
echo "📋 Checking main nginx.conf include statements:"
grep -A 5 -B 2 "include" /etc/nginx/nginx.conf
echo ""
echo "📋 Checking what nginx is actually serving:"
curl -s http://localhost/ | head -5
echo ""
echo "📋 Checking if our app config exists:"
ls -la /etc/nginx/conf.d/app.conf 2>/dev/null || echo "No app.conf in conf.d"
ls -la /etc/nginx/sites-enabled/app 2>/dev/null || echo "No app in sites-enabled"
'''
    
    result = run_remote_command(instance_ip, command)
    if result:
        print("STDOUT:")
        print(result['stdout'])
        if result['stderr']:
            print("STDERR:")
            print(result['stderr'])
        print(f"Status: {result['status']}")
    print()

if __name__ == "__main__":
    # Check both instances
    check_nginx_config('18.232.114.213', 'python-flask-api-v6')
    check_nginx_config('35.171.85.222', 'react-dashboard-v6')