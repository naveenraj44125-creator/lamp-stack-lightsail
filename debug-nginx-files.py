#!/usr/bin/env python3
"""
Debug where nginx files actually are
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'nginx-static-demo'
    region = 'us-east-1'
    
    print("🔍 Debugging Nginx File Location")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    debug_script = '''
echo "📋 Checking /var/www/html:"
ls -laR /var/www/html/

echo ""
echo "📋 Looking for index.html:"
find /var/www -name "index.html" 2>/dev/null || echo "No index.html found in /var/www"

echo ""
echo "📋 Looking for HTML files:"
find /var/www -name "*.html" 2>/dev/null || echo "No HTML files found in /var/www"

echo ""
echo "📋 Checking /opt:"
ls -la /opt/ 2>/dev/null || echo "/opt not found"

echo ""
echo "📋 Checking nginx config:"
cat /etc/nginx/sites-enabled/app 2>/dev/null || cat /etc/nginx/sites-enabled/default 2>/dev/null || echo "No nginx site config found"

echo ""
echo "📋 Checking recent deployments:"
ls -lat /tmp/*.tar.gz 2>/dev/null | head -5 || echo "No deployment packages in /tmp"
'''
    
    success, output = client.run_command(debug_script, timeout=60)
    print(output)

if __name__ == '__main__':
    main()
