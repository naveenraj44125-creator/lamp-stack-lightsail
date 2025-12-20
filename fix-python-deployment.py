#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workflows.lightsail_common import LightsailBase

client = LightsailBase('python-flask-api-v6', 'us-east-1')
script = '''
echo "🔧 Fixing Python Flask deployment..."

# 1. Install Flask and gunicorn in the virtual environment
echo "📦 Installing packages in virtual environment..."
/opt/python-venv/app/bin/pip install Flask gunicorn

# 2. Fix log directory permissions
echo "📁 Fixing log directory permissions..."
sudo mkdir -p /var/log/python-app
sudo chown ec2-user:ec2-user /var/log/python-app
sudo chmod 755 /var/log/python-app

# 3. Update systemd service to use virtual environment
echo "⚙️ Updating systemd service configuration..."
sudo tee /etc/systemd/system/python-app.service > /dev/null << 'EOF'
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

# 4. Reload systemd and restart service
echo "🔄 Reloading systemd and restarting service..."
sudo systemctl daemon-reload
sudo systemctl stop python-app
sudo systemctl start python-app
sudo systemctl status python-app --no-pager

# 5. Test the application
echo "🧪 Testing application..."
sleep 5
curl -I http://localhost:5000/ 2>&1 | head -5

echo "✅ Python deployment fix complete!"
'''
success, output = client.run_command(script, timeout=180)
print(output)