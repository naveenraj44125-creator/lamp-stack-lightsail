#!/usr/bin/env python3
"""
Final fix for Python Flask external connectivity
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'python-flask-api-v6'
    region = 'us-east-1'
    
    print(f"\n🔧 Final Python Connectivity Fix for {instance_name}")
    print("=" * 70)
    
    client = LightsailBase(instance_name, region)
    
    # Comprehensive fix for Python connectivity
    fix_script = '''
set -e
echo "🔧 Final Python connectivity fix..."

APP_DIR="/opt/python-app"
VENV_DIR="/opt/python-venv/app"

# 1. Stop the service first
echo "🛑 Stopping Python service..."
sudo systemctl stop python-app.service

# 2. Check what's actually listening on port 5000
echo "🔍 Checking what was listening on port 5000..."
sudo ss -tlnp | grep :5000 || echo "Nothing on port 5000"

# 3. Kill any remaining Python processes
echo "🧹 Cleaning up any remaining Python processes..."
sudo pkill -f gunicorn || echo "No gunicorn processes to kill"
sudo pkill -f "python.*app.py" || echo "No Python app processes to kill"

# 4. Wait a moment
sleep 3

# 5. Update the systemd service with explicit binding and better configuration
echo "🔧 Creating optimized systemd service..."
sudo tee /etc/systemd/system/python-app.service > /dev/null << 'EOF'
[Unit]
Description=Python Flask Application
After=network.target

[Service]
Type=simple
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/python-app
Environment=PATH=/opt/python-venv/app/bin:/usr/bin:/usr/local/bin
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production
Environment=PORT=5000
Environment=PYTHONPATH=/opt/python-app
ExecStart=/opt/python-venv/app/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 --keep-alive 2 --max-requests 1000 --preload --access-logfile /var/log/python-app/access.log --error-logfile /var/log/python-app/error.log app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10
StandardOutput=append:/var/log/python-app/output.log
StandardError=append:/var/log/python-app/stderr.log

[Install]
WantedBy=multi-user.target
EOF

# 6. Ensure log directory permissions
echo "📁 Setting up log directory..."
sudo mkdir -p /var/log/python-app
sudo chown -R ec2-user:ec2-user /var/log/python-app
sudo chmod 755 /var/log/python-app

# 7. Ensure app directory permissions
echo "📁 Setting up app directory permissions..."
sudo chown -R ec2-user:ec2-user "$APP_DIR"
sudo chown -R ec2-user:ec2-user "$VENV_DIR"

# 8. Test the Flask app directly first
echo "🧪 Testing Flask app import..."
cd "$APP_DIR"
source "$VENV_DIR/bin/activate"
python -c "
import sys
sys.path.insert(0, '/opt/python-app')
try:
    import app
    print('✅ Flask app imports successfully')
    print('Flask app object:', app.app)
    print('Available routes:')
    for rule in app.app.url_map.iter_rules():
        print(f'  {rule.rule} -> {rule.endpoint}')
except Exception as e:
    print('❌ Flask app import failed:', str(e))
    import traceback
    traceback.print_exc()
"
deactivate

# 9. Reload systemd and start service
echo "🔄 Starting Python service with new configuration..."
sudo systemctl daemon-reload
sudo systemctl enable python-app.service
sudo systemctl start python-app.service

# 10. Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 15

# 11. Check service status
if systemctl is-active --quiet python-app.service; then
    echo "✅ Python service is running"
    
    # Check what's listening
    echo "🔍 Checking listening ports..."
    sudo ss -tlnp | grep :5000 || echo "❌ Nothing listening on port 5000"
    
    # Test local connection
    echo "🧪 Testing local connection..."
    sleep 5
    if curl -s -f http://localhost:5000/ > /tmp/local-test.html; then
        echo "✅ Local connection successful"
        echo "Response preview:"
        head -2 /tmp/local-test.html
    else
        echo "❌ Local connection failed"
        echo "Checking what's actually running:"
        ps aux | grep gunicorn | grep -v grep || echo "No gunicorn processes"
    fi
    
    # Test health endpoint
    if curl -s -f http://localhost:5000/api/health > /tmp/health.json; then
        echo "✅ Health endpoint working:"
        cat /tmp/health.json
    else
        echo "❌ Health endpoint not responding"
    fi
    
else
    echo "❌ Python service failed to start"
    echo "Service status:"
    sudo systemctl status python-app.service --no-pager
    echo ""
    echo "Recent logs:"
    sudo journalctl -u python-app.service -n 30 --no-pager
    echo ""
    echo "Error log:"
    sudo cat /var/log/python-app/error.log 2>/dev/null || echo "No error log"
    exit 1
fi

# 12. Test external connectivity
echo ""
echo "🌐 Testing external connectivity..."
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")
if [ -n "$PUBLIC_IP" ]; then
    echo "Public IP: $PUBLIC_IP"
    if curl -s -f "http://$PUBLIC_IP/" > /tmp/external-test.html; then
        echo "✅ External HTTP access successful!"
        echo "Response preview:"
        head -2 /tmp/external-test.html
    else
        echo "❌ External HTTP access failed"
        echo "Checking nginx configuration and logs..."
        
        # Check nginx config
        echo "Nginx configuration test:"
        sudo nginx -t
        
        echo ""
        echo "Nginx app.conf:"
        sudo cat /etc/nginx/conf.d/app.conf 2>/dev/null || echo "No app.conf found"
        
        echo ""
        echo "Recent nginx error log:"
        sudo tail -5 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error log"
        
        # Test direct connection to see if it's a nginx issue
        echo ""
        echo "Testing direct connection to Flask (bypassing nginx):"
        if curl -s -f "http://$PUBLIC_IP:5000/" > /tmp/direct-test.html 2>/dev/null; then
            echo "✅ Direct connection to Flask works - nginx proxy issue"
        else
            echo "❌ Direct connection also fails - Flask binding issue"
        fi
    fi
else
    echo "❌ Could not get public IP"
fi

echo ""
echo "✅ Final Python fix complete!"
'''
    
    success, output = client.run_command(fix_script, timeout=300)
    print(output)
    
    if success:
        print("\n✅ Python deployment should now be fully functional!")
    else:
        print("\n❌ Final fix encountered issues")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())