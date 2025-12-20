#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workflows.lightsail_common import LightsailBase

client = LightsailBase('python-flask-api-v6', 'us-east-1')
script = '''
echo "=== Checking nginx configuration directories ==="
ls -la /etc/nginx/conf.d/ 2>/dev/null || echo "No conf.d directory"
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "No sites-enabled directory"
ls -la /etc/nginx/sites-available/ 2>/dev/null || echo "No sites-available directory"

echo ""
echo "=== Checking application directories ==="
ls -la /opt/ 2>/dev/null || echo "No /opt directory"
ls -la /var/www/ 2>/dev/null || echo "No /var/www directory"

echo ""
echo "=== Checking deployment package ==="
ls -la /tmp/deployment-package/ 2>/dev/null || echo "No deployment package"
ls -la /tmp/deployment-package.tar.gz 2>/dev/null || echo "No deployment tar.gz"

echo ""
echo "=== Checking systemd services ==="
sudo systemctl list-unit-files | grep -E "gunicorn|python|flask" || echo "No Python services found"

echo ""
echo "=== Checking Python configurator logs ==="
sudo journalctl -u python-app --no-pager -n 50 2>/dev/null || echo "No python-app service logs"
'''
success, output = client.run_command(script, timeout=60)
print(output)
