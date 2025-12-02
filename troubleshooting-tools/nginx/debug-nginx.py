#!/usr/bin/env python3
"""
Comprehensive Nginx deployment debug script
Checks files, permissions, nginx config, and service status
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [nginx-static-demo]: ").strip() or 'nginx-static-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print("\n🔍 Debugging Nginx Deployment")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    debug_script = '''
echo "📋 1. Checking /var/www/html structure:"
ls -laR /var/www/html/ | head -50

echo ""
echo "📋 2. Finding HTML files:"
find /var/www -name "*.html" -ls 2>/dev/null || echo "No HTML files found"

echo ""
echo "📋 3. Checking nginx configuration:"
cat /etc/nginx/sites-enabled/app 2>/dev/null || cat /etc/nginx/sites-enabled/default 2>/dev/null

echo ""
echo "📋 4. Testing nginx config:"
sudo nginx -t

echo ""
echo "📋 5. Checking nginx service status:"
sudo systemctl status nginx --no-pager

echo ""
echo "📋 6. Checking nginx error log (last 20 lines):"
sudo tail -20 /var/log/nginx/error.log

echo ""
echo "📋 7. Checking nginx access log (last 10 lines):"
sudo tail -10 /var/log/nginx/access.log

echo ""
echo "📋 8. Checking file permissions:"
ls -la /var/www/html/

echo ""
echo "📋 9. Checking recent deployments:"
ls -lat /tmp/*.tar.gz 2>/dev/null | head -5 || echo "No deployment packages"

echo ""
echo "📋 10. Testing local curl:"
curl -I http://localhost/ 2>&1 | head -10
'''
    
    success, output = client.run_command(debug_script, timeout=120)
    print(output)
    
    if not success:
        print("\n❌ Debug script failed")
        return 1
    
    print("\n✅ Debug complete")
    return 0

if __name__ == '__main__':
    sys.exit(main())
