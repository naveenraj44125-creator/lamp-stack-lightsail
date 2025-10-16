#!/usr/bin/env python3
"""
Verification script for LAMP Stack deployment on AWS Lightsail
This script only performs health checks and verification without deploying anything
"""

import sys
import argparse
from lightsail_common import create_lightsail_client

class LightsailVerifier:
    def __init__(self, instance_name, region='us-east-1'):
        self.client = create_lightsail_client(instance_name, region, 'lamp')

    def verify_lamp_stack(self):
        """Verify LAMP stack components are running"""
        return self.client.verify_lamp_stack()

    def verify_application_health(self):
        """Verify application health and accessibility"""
        try:
            # Get instance info using common functionality
            instance_info = self.client.get_instance_info()
            if not instance_info:
                print("❌ Failed to get instance information")
                return False
            
            public_ip = instance_info['public_ip']
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
            
            success, output = self.client.run_command(health_script, timeout=120, max_retries=3, show_output_lines=10)
            
            if success:
                print(f"✅ Application health check completed")
                print(f"🌐 Application URL: http://{public_ip}/")
            
            return success
            
        except Exception as e:
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
        
        success, output = self.client.run_command(security_script, timeout=120, max_retries=3, show_output_lines=10)
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
