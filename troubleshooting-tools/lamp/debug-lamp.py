#!/usr/bin/env python3
"""
Comprehensive LAMP stack deployment debug script
Checks Apache, MySQL, PHP, and application files
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [lamp-stack-demo]: ").strip() or 'lamp-stack-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print("\n🔍 Debugging LAMP Stack Deployment")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    debug_script = '''
echo "📋 1. Checking Apache status:"
sudo systemctl status apache2 --no-pager || sudo systemctl status httpd --no-pager

echo ""
echo "📋 2. Checking PHP version:"
php -v

echo ""
echo "📋 3. Checking MySQL/MariaDB status:"
sudo systemctl status mysql --no-pager || sudo systemctl status mariadb --no-pager

echo ""
echo "📋 4. Checking /var/www/html structure:"
ls -laR /var/www/html/ | head -50

echo ""
echo "📋 5. Checking Apache configuration:"
apache2ctl -S 2>&1 || httpd -S 2>&1

echo ""
echo "📋 6. Checking Apache error log (last 20 lines):"
sudo tail -20 /var/log/apache2/error.log 2>/dev/null || sudo tail -20 /var/log/httpd/error_log 2>/dev/null

echo ""
echo "📋 7. Checking Apache access log (last 10 lines):"
sudo tail -10 /var/log/apache2/access.log 2>/dev/null || sudo tail -10 /var/log/httpd/access_log 2>/dev/null

echo ""
echo "📋 8. Testing PHP:"
php -r "echo 'PHP is working: ' . phpversion() . PHP_EOL;"

echo ""
echo "📋 9. Checking PHP modules:"
php -m | head -20

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
