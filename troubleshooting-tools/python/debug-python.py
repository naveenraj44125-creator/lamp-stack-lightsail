#!/usr/bin/env python3
"""
Comprehensive Python/Flask deployment debug script
Checks Python, Flask, Gunicorn, and application status
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [python-app-demo]: ").strip() or 'python-app-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print("\n🔍 Debugging Python/Flask Deployment")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    debug_script = '''
echo "📋 1. Checking Python version:"
python3 --version

echo ""
echo "📋 2. Checking pip packages:"
pip3 list | grep -E "Flask|gunicorn|requests"

echo ""
echo "📋 3. Checking Gunicorn service status:"
sudo systemctl status gunicorn --no-pager

echo ""
echo "📋 4. Checking Nginx status:"
sudo systemctl status nginx --no-pager

echo ""
echo "📋 5. Checking application directory:"
ls -la /opt/app/ 2>/dev/null || ls -la /var/www/app/ 2>/dev/null || echo "App directory not found"

echo ""
echo "📋 6. Checking Gunicorn socket:"
sudo systemctl status gunicorn.socket --no-pager 2>/dev/null || echo "No gunicorn socket"

echo ""
echo "📋 7. Checking Gunicorn logs (last 30 lines):"
sudo journalctl -u gunicorn --no-pager -n 30

echo ""
echo "📋 8. Checking Nginx error log (last 20 lines):"
sudo tail -20 /var/log/nginx/error.log

echo ""
echo "📋 9. Checking Nginx configuration:"
cat /etc/nginx/sites-enabled/app 2>/dev/null || cat /etc/nginx/sites-enabled/default 2>/dev/null

echo ""
echo "📋 10. Testing local curl:"
curl -I http://localhost/ 2>&1 | head -10

echo ""
echo "📋 11. Checking Python app process:"
ps aux | grep -E "gunicorn|python" | grep -v grep
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
