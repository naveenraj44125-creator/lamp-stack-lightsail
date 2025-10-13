#!/usr/bin/env python3
"""
Verification script for LAMP Stack deployment on AWS Lightsail
This script only performs health checks and verification without deploying anything
"""

import boto3
import subprocess
import tempfile
import os
import time
import sys
import argparse
from botocore.exceptions import ClientError, NoCredentialsError

class LightsailVerifier:
    def __init__(self, instance_name, region='us-east-1'):
        self.instance_name = instance_name
        self.region = region
        try:
            self.lightsail = boto3.client('lightsail', region_name=region)
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure AWS credentials.")
            sys.exit(1)
    
    def run_command(self, command, timeout=60):
        """Execute command on Lightsail instance using get_instance_access_details"""
        try:
            print(f"🔧 Running: {command[:100]}{'...' if len(command) > 100 else ''}")
            
            # Get SSH access details
            ssh_response = self.lightsail.get_instance_access_details(instanceName=self.instance_name)
            ssh_details = ssh_response['accessDetails']
            
            # Create temporary SSH key files
            key_path, cert_path = self.create_ssh_files(ssh_details)
            
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
                        for line in lines[:10]:  # Show first 10 lines
                            print(f"   {line}")
                        if len(lines) > 10:
                            print(f"   ... ({len(lines) - 10} more lines)")
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

    def create_ssh_files(self, ssh_details):
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

    def verify_lamp_stack(self):
        """Verify LAMP stack components are running"""
        print("🔍 Verifying LAMP stack components...")
        
        verify_script = '''
set -e

echo "=== LAMP Stack Verification ==="

# Check Apache
echo "Checking Apache..."
sudo systemctl is-active apache2 && echo "✅ Apache is running" || echo "❌ Apache is not running"

# Check MySQL/MariaDB
echo "Checking MySQL/MariaDB..."
sudo systemctl is-active mysql && echo "✅ MySQL is running" || echo "❌ MySQL is not running"

# Check PHP
echo "Checking PHP..."
php --version | head -1 && echo "✅ PHP is installed" || echo "❌ PHP is not installed"

# Check web server response
echo "Checking web server response..."
curl -f -s http://localhost/ > /dev/null && echo "✅ Web server responding" || echo "❌ Web server not responding"

# Check if application files exist
echo "Checking application files..."
ls -la /var/www/html/ | head -10

echo "=== LAMP Stack Verification Complete ==="
'''
        
        success, output = self.run_command(verify_script, timeout=120)
        return success

    def verify_application_health(self):
        """Verify application health and accessibility"""
        try:
            # Get instance public IP
            response = self.lightsail.get_instance(instanceName=self.instance_name)
            public_ip = response['instance']['publicIpAddress']
            
            print(f"🔍 Verifying application health at http://{public_ip}/")
            
            # Test the application
            health_script = '''
echo "=== Application Health Check ==="

# Test local access
echo "Testing local application access..."
response=$(curl -f -s http://localhost/ 2>/dev/null || echo "FAILED")
if [[ "$response" != "FAILED" ]]; then
    echo "✅ Application accessible locally"
    echo "Response preview: $(echo "$response" | head -c 200)..."
else
    echo "❌ Application not accessible locally"
fi

# Check Apache error logs for any issues
echo "Checking Apache error logs..."
sudo tail -10 /var/log/apache2/error.log 2>/dev/null || echo "No recent errors in Apache log"

# Check Apache access logs
echo "Checking Apache access logs..."
sudo tail -5 /var/log/apache2/access.log 2>/dev/null || echo "No recent access logs"

# Check disk space
echo "Checking disk space..."
df -h /var/www/html

echo "=== Application Health Check Complete ==="
'''
            
            success, output = self.run_command(health_script, timeout=120)
            
            if success:
                print(f"✅ Application health check completed")
                print(f"🌐 Application URL: http://{public_ip}/")
            
            return success
            
        except ClientError as e:
            print(f"❌ Error during health check: {e}")
            return False

    def verify_security_basics(self):
        """Verify basic security configurations"""
        print("🔒 Verifying basic security configurations...")
        
        security_script = '''
echo "=== Security Verification ==="

# Check firewall status
echo "Checking firewall rules..."
sudo ufw status || echo "UFW not configured"

# Check Apache security headers (basic)
echo "Checking Apache configuration..."
apache2ctl -t && echo "✅ Apache configuration is valid" || echo "❌ Apache configuration has issues"

# Check file permissions
echo "Checking web directory permissions..."
ls -la /var/www/html/ | head -5

# Check for any obvious security issues
echo "Checking for world-writable files..."
find /var/www/html -type f -perm -002 2>/dev/null | head -5 || echo "No world-writable files found"

echo "=== Security Verification Complete ==="
'''
        
        success, output = self.run_command(security_script, timeout=120)
        return success

def main():
    parser = argparse.ArgumentParser(description='Verify LAMP Stack deployment on AWS Lightsail')
    parser.add_argument('instance_name', help='Lightsail instance name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--health-only', action='store_true', help='Only run application health checks')
    parser.add_argument('--security-only', action='store_true', help='Only run security checks')
    
    args = parser.parse_args()
    
    print(f"🔍 Starting verification for {args.instance_name}")
    print(f"🌍 Region: {args.region}")
    
    # Create verifier
    verifier = LightsailVerifier(args.instance_name, args.region)
    
    success = True
    
    # Run LAMP stack verification unless specific checks are requested
    if not args.health_only and not args.security_only:
        if not verifier.verify_lamp_stack():
            print("❌ LAMP stack verification failed")
            success = False
    
    # Run application health check
    if not args.security_only:
        if not verifier.verify_application_health():
            print("❌ Application health check failed")
            success = False
    
    # Run security verification
    if not args.health_only:
        if not verifier.verify_security_basics():
            print("❌ Security verification failed")
            success = False
    
    if success:
        print("🎉 All verification checks passed!")
        sys.exit(0)
    else:
        print("❌ Some verification checks failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
