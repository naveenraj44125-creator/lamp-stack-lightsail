#!/usr/bin/env python3
"""
Debug Python Flask connectivity issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'python-flask-api-v6'
    region = 'us-east-1'
    
    print(f"\n🔍 Debugging Python Connectivity for {instance_name}")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    debug_script = '''
echo "🔍 Debugging Python Flask connectivity..."

echo ""
echo "1. Checking what's listening on port 5000:"
sudo ss -tlnp | grep :5000 || echo "Nothing listening on port 5000"

echo ""
echo "2. Checking all Python processes:"
ps aux | grep python | grep -v grep || echo "No Python processes found"

echo ""
echo "3. Checking gunicorn processes:"
ps aux | grep gunicorn | grep -v grep || echo "No gunicorn processes found"

echo ""
echo "4. Testing direct connection to Flask app:"
curl -v http://127.0.0.1:5000/ 2>&1 | head -20

echo ""
echo "5. Checking Python service logs:"
sudo journalctl -u python-app.service -n 10 --no-pager

echo ""
echo "6. Checking if Flask is binding to all interfaces:"
sudo netstat -tlnp | grep :5000 || echo "netstat not available, using ss"
sudo ss -tlnp | grep :5000

echo ""
echo "7. Checking nginx configuration:"
sudo nginx -t
echo ""
echo "Nginx app.conf:"
sudo cat /etc/nginx/conf.d/app.conf 2>/dev/null || echo "No app.conf found"

echo ""
echo "8. Testing if we can reach Flask from nginx perspective:"
curl -v http://localhost:5000/ 2>&1 | head -10

echo ""
echo "9. Checking firewall status:"
sudo iptables -L -n | head -10 || echo "iptables not available"

echo ""
echo "10. Checking if service is actually running and what port it's using:"
sudo systemctl status python-app.service --no-pager | head -10
'''
    
    success, output = client.run_command(debug_script, timeout=120)
    print(output)
    
    # Now try to fix the binding issue
    print("\n🔧 Attempting to fix Flask binding issue...")
    
    fix_script = '''
echo "🔧 Fixing Flask binding to ensure it listens on all interfaces..."

# Check current service configuration
echo "Current service configuration:"
cat /etc/systemd/system/python-app.service | grep ExecStart

echo ""
echo "🔧 Updating service to ensure proper binding..."
sudo tee /etc/systemd/system/python-app.service > /dev/null << EOF
[Unit]
Description=Python Flask Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/python-app
Environment=PATH=/opt/python-venv/app/bin:/usr/bin:/usr/local/bin
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production
Environment=PORT=5000
ExecStart=/opt/python-venv/app/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 --access-logfile /var/log/python-app/access.log --error-logfile /var/log/python-app/error.log app:app
Restart=always
RestartSec=10
StandardOutput=append:/var/log/python-app/output.log
StandardError=append:/var/log/python-app/stderr.log

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "🔄 Restarting service with new configuration..."
sudo systemctl daemon-reload
sudo systemctl stop python-app.service
sleep 5
sudo systemctl start python-app.service

# Wait for service to start
sleep 10

echo ""
echo "🧪 Testing after restart..."
if systemctl is-active --quiet python-app.service; then
    echo "✅ Service is running"
    
    # Check what's listening
    echo "Checking what's listening on port 5000:"
    sudo ss -tlnp | grep :5000
    
    # Test local connection
    sleep 5
    if curl -s -f http://localhost:5000/ > /tmp/test.html; then
        echo "✅ Local connection works"
    else
        echo "❌ Local connection still fails"
    fi
    
    # Test external connection
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    echo "Testing external connection to $PUBLIC_IP..."
    if curl -s -f "http://$PUBLIC_IP/" > /tmp/external.html; then
        echo "✅ External connection works!"
        head -3 /tmp/external.html
    else
        echo "❌ External connection still fails"
        echo "Checking nginx error log:"
        sudo tail -5 /var/log/nginx/error.log
    fi
else
    echo "❌ Service failed to start"
    sudo systemctl status python-app.service --no-pager
    sudo journalctl -u python-app.service -n 20 --no-pager
fi
'''
    
    success, output = client.run_command(fix_script, timeout=180)
    print(output)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())