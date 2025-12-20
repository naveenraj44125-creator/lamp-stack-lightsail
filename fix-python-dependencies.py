#!/usr/bin/env python3
"""
Fix Python Flask deployment by installing missing dependencies
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'python-flask-api-v6'  # From deployment config
    region = 'us-east-1'
    
    print(f"\n🔧 Fixing Python Dependencies for {instance_name}")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    # First check current status
    status_script = '''
echo "🔍 Checking current Python application status..."
echo ""

# Check if app directory exists
APP_DIR="/opt/python-app"
if [ -d "$APP_DIR" ]; then
    echo "✅ Application directory exists: $APP_DIR"
    ls -la "$APP_DIR"
else
    echo "❌ Application directory not found: $APP_DIR"
    exit 1
fi

echo ""
echo "🔍 Checking requirements.txt..."
if [ -f "$APP_DIR/requirements.txt" ]; then
    echo "✅ requirements.txt found:"
    cat "$APP_DIR/requirements.txt"
else
    echo "❌ requirements.txt not found"
fi

echo ""
echo "🔍 Checking Python service status..."
if systemctl is-active --quiet python-app.service; then
    echo "✅ Python service is running"
else
    echo "❌ Python service is not running"
    echo "Service status:"
    sudo systemctl status python-app.service --no-pager | head -10
fi

echo ""
echo "🔍 Checking what's installed globally..."
pip3 list | grep -E "(Flask|psutil|gunicorn)" || echo "No relevant packages found globally"

echo ""
echo "🔍 Checking virtual environment..."
if [ -d "/opt/python-venv/app" ]; then
    echo "✅ Virtual environment exists"
    source /opt/python-venv/app/bin/activate
    pip list | grep -E "(Flask|psutil|gunicorn)" || echo "No relevant packages found in venv"
    deactivate
else
    echo "❌ Virtual environment not found at /opt/python-venv/app"
fi
'''
    
    print("📊 Checking current status...")
    success, output = client.run_command(status_script, timeout=60)
    print(output)
    
    # Now fix the dependencies
    fix_script = '''
set -e
APP_DIR="/opt/python-app"
VENV_DIR="/opt/python-venv/app"

echo ""
echo "🔧 Installing missing Python dependencies..."

# Ensure we have the latest pip
echo "📦 Updating pip..."
sudo pip3 install --upgrade pip

# Install dependencies globally first (fallback)
echo "📦 Installing dependencies globally..."
cd "$APP_DIR"
sudo pip3 install -r requirements.txt --force-reinstall

# Create/recreate virtual environment if needed
echo "📦 Setting up virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    sudo mkdir -p /opt/python-venv
    sudo python3 -m venv "$VENV_DIR"
    sudo chown -R ubuntu:ubuntu /opt/python-venv
fi

# Install dependencies in virtual environment
echo "📦 Installing dependencies in virtual environment..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt" --force-reinstall
deactivate

echo ""
echo "🔧 Updating systemd service to use virtual environment..."
sudo tee /etc/systemd/system/python-app.service > /dev/null << EOF
[Unit]
Description=Python Flask Application
After=network.target

[Service]
Type=simple
User=ubuntu
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
echo "🔄 Reloading and restarting Python service..."
sudo systemctl daemon-reload
sudo systemctl stop python-app.service 2>/dev/null || true
sudo systemctl start python-app.service

# Wait and check status
sleep 10

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
        sudo ss -tlnp | grep python || echo "No python processes found"
    fi
else
    echo "❌ Python service failed to start"
    echo "Service status:"
    sudo systemctl status python-app.service --no-pager
    echo ""
    echo "Recent logs:"
    sudo journalctl -u python-app.service -n 20 --no-pager
fi

echo ""
echo "🔧 Ensuring nginx is properly configured and running..."
sudo systemctl reload nginx
sudo systemctl status nginx --no-pager | head -5

echo ""
echo "✅ Python dependency fix complete!"
'''
    
    print("\n🔧 Installing missing dependencies and fixing service...")
    success, output = client.run_command(fix_script, timeout=300)
    print(output)
    
    if success:
        print("\n✅ Python dependencies fixed successfully!")
        
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
    echo "Checking nginx error logs:"
    sudo tail -10 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error log"
fi
'''
        
        success, output = client.run_command(test_script, timeout=60)
        print(output)
        
    else:
        print("\n❌ Failed to fix Python dependencies")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())