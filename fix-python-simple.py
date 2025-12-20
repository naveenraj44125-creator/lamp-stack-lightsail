#!/usr/bin/env python3
"""
Simple Python Flask deployment fix - avoid pip upgrade issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'python-flask-api-v6'
    region = 'us-east-1'
    
    print(f"\n🔧 Simple Python Fix for {instance_name}")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    # Fix without pip upgrade
    fix_script = '''
set -e
APP_DIR="/opt/python-app"
VENV_DIR="/opt/python-venv/app"

echo "🔧 Fixing Python service without pip upgrade..."

# Check if psutil is missing in venv
echo "📦 Checking virtual environment dependencies..."
source "$VENV_DIR/bin/activate"
if ! python -c "import psutil" 2>/dev/null; then
    echo "❌ psutil missing in venv, installing..."
    pip install psutil==5.9.6
else
    echo "✅ psutil already available in venv"
fi

if ! python -c "import werkzeug" 2>/dev/null; then
    echo "❌ werkzeug missing in venv, installing..."
    pip install Werkzeug==3.0.1
else
    echo "✅ werkzeug already available in venv"
fi
deactivate

echo ""
echo "🔧 Fixing systemd service user (should be ec2-user on Amazon Linux)..."
sudo tee /etc/systemd/system/python-app.service > /dev/null << EOF
[Unit]
Description=Python Flask Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=$APP_DIR
Environment=PATH=$VENV_DIR/bin:/usr/bin:/usr/local/bin
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production
Environment=PORT=5000
ExecStart=$VENV_DIR/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 --access-logfile /var/log/python-app/access.log --error-logfile /var/log/python-app/error.log app:app
Restart=always
RestartSec=10
StandardOutput=append:/var/log/python-app/output.log
StandardError=append:/var/log/python-app/stderr.log

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "🔧 Ensuring log directory has correct permissions..."
sudo mkdir -p /var/log/python-app
sudo chown -R ec2-user:ec2-user /var/log/python-app

echo ""
echo "🔄 Reloading and restarting Python service..."
sudo systemctl daemon-reload
sudo systemctl stop python-app.service 2>/dev/null || true
sleep 3
sudo systemctl start python-app.service

# Wait and check status
sleep 15

if systemctl is-active --quiet python-app.service; then
    echo "✅ Python service started successfully"
    
    # Test if it's listening on port 5000
    sleep 5
    if sudo ss -tlnp | grep -q ":5000"; then
        echo "✅ Application is listening on port 5000"
        
        # Test local connection
        echo "🧪 Testing local Flask application..."
        if curl -s -f http://localhost:5000/ > /tmp/flask-test.html; then
            echo "✅ Local connection successful"
            echo "Response preview:"
            head -3 /tmp/flask-test.html
        else
            echo "❌ Local connection failed"
            echo "Checking what's on port 5000:"
            sudo ss -tlnp | grep :5000 || echo "Nothing on port 5000"
        fi
        
        # Test health endpoint
        if curl -s -f http://localhost:5000/api/health > /tmp/health-test.json; then
            echo "✅ Health endpoint responding:"
            cat /tmp/health-test.json
        else
            echo "⚠️ Health endpoint not responding"
        fi
    else
        echo "❌ Application not listening on port 5000"
        echo "Checking all listening ports:"
        sudo ss -tlnp | head -10
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
    echo ""
    echo "Stderr log:"
    sudo cat /var/log/python-app/stderr.log 2>/dev/null || echo "No stderr log"
fi

echo ""
echo "🔧 Testing Flask app import directly..."
cd "$APP_DIR"
source "$VENV_DIR/bin/activate"
python -c "
try:
    import app
    print('✅ Flask app imports successfully')
    print('Available routes:', [str(rule) for rule in app.app.url_map.iter_rules()])
except Exception as e:
    print('❌ Flask app import failed:', str(e))
    import traceback
    traceback.print_exc()
"
deactivate

echo ""
echo "✅ Simple Python fix complete!"
'''
    
    success, output = client.run_command(fix_script, timeout=300)
    print(output)
    
    if success:
        print("\n✅ Python service fixed!")
        
        # Test external connectivity
        print("\n🧪 Testing external connectivity...")
        test_script = '''
echo "Testing external HTTP access..."
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "Public IP: $PUBLIC_IP"

if curl -s -f "http://$PUBLIC_IP/" > /tmp/external-test.html; then
    echo "✅ External HTTP access successful"
    echo "Response preview:"
    head -3 /tmp/external-test.html
else
    echo "❌ External HTTP access failed"
    echo "Checking nginx status:"
    sudo systemctl status nginx --no-pager | head -5
    echo ""
    echo "Checking nginx error logs:"
    sudo tail -10 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error log"
fi
'''
        
        success, output = client.run_command(test_script, timeout=60)
        print(output)
        
    else:
        print("\n❌ Failed to fix Python service")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())