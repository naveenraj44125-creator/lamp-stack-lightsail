#!/usr/bin/env python3
"""
Comprehensive React deployment debug script
Checks build files, Nginx configuration, and static file serving
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [react-app-demo]: ").strip() or 'react-app-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print("\n🔍 Debugging React Deployment")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    debug_script = '''
echo "📋 1. Checking /var/www/html structure:"
ls -laR /var/www/html/ | head -50

echo ""
echo "📋 2. Checking for React build files:"
ls -la /var/www/html/static/ 2>/dev/null || echo "No static directory found"

echo ""
echo "📋 3. Checking for index.html:"
cat /var/www/html/index.html 2>/dev/null | head -20 || echo "No index.html found"

echo ""
echo "📋 4. Checking Nginx status:"
sudo systemctl status nginx --no-pager

echo ""
echo "📋 5. Checking Nginx configuration:"
cat /etc/nginx/sites-enabled/app 2>/dev/null || cat /etc/nginx/sites-enabled/default 2>/dev/null

echo ""
echo "📋 6. Testing Nginx config:"
sudo nginx -t

echo ""
echo "📋 7. Checking Nginx error log (last 20 lines):"
sudo tail -20 /var/log/nginx/error.log

echo ""
echo "📋 8. Checking Nginx access log (last 10 lines):"
sudo tail -10 /var/log/nginx/access.log

echo ""
echo "📋 9. Checking file permissions:"
ls -la /var/www/html/

echo ""
echo "📋 10. Testing local curl:"
curl -I http://localhost/ 2>&1 | head -10

echo ""
echo "📋 11. Checking for JavaScript files:"
find /var/www/html -name "*.js" -type f | head -10

echo ""
echo "📋 12. Checking for CSS files:"
find /var/www/html -name "*.css" -type f | head -10
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
