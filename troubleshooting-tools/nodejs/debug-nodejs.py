#!/usr/bin/env python3
"""
Comprehensive Node.js deployment debug script
Checks Node.js, npm, PM2, and application status
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [nodejs-app-demo]: ").strip() or 'nodejs-app-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print("\n🔍 Debugging Node.js Deployment")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    debug_script = '''
echo "📋 1. Checking Node.js version:"
node --version

echo ""
echo "📋 2. Checking npm version:"
npm --version

echo ""
echo "📋 3. Checking PM2 status:"
pm2 status

echo ""
echo "📋 4. Checking PM2 logs (last 30 lines):"
pm2 logs --lines 30 --nostream

echo ""
echo "📋 5. Checking application directory:"
ls -la /opt/app/ 2>/dev/null || ls -la /var/www/app/ 2>/dev/null || echo "App directory not found"

echo ""
echo "📋 6. Checking package.json:"
cat /opt/app/package.json 2>/dev/null || cat /var/www/app/package.json 2>/dev/null || echo "package.json not found"

echo ""
echo "📋 7. Checking installed npm packages:"
npm list --depth=0 2>/dev/null | head -20

echo ""
echo "📋 8. Checking Nginx status:"
sudo systemctl status nginx --no-pager

echo ""
echo "📋 9. Checking Nginx configuration:"
cat /etc/nginx/sites-enabled/app 2>/dev/null || cat /etc/nginx/sites-enabled/default 2>/dev/null

echo ""
echo "📋 10. Checking Nginx error log (last 20 lines):"
sudo tail -20 /var/log/nginx/error.log

echo ""
echo "📋 11. Testing local curl:"
curl -I http://localhost/ 2>&1 | head -10

echo ""
echo "📋 12. Checking Node.js process:"
ps aux | grep node | grep -v grep
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
