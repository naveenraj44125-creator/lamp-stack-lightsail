#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workflows.lightsail_common import LightsailBase

client = LightsailBase('python-flask-api-v6', 'us-east-1')
script = '''
echo "🔧 Fixing Python permissions and virtual environment..."

# 1. Fix ownership of virtual environment
echo "👤 Fixing virtual environment ownership..."
sudo chown -R ec2-user:ec2-user /opt/python-venv/
sudo chown -R ec2-user:ec2-user /opt/python-app/

# 2. Install packages as ec2-user
echo "📦 Installing packages in virtual environment as ec2-user..."
sudo -u ec2-user /opt/python-venv/app/bin/pip install Flask gunicorn

# 3. Test if gunicorn works
echo "🧪 Testing gunicorn installation..."
sudo -u ec2-user /opt/python-venv/app/bin/gunicorn --version

# 4. Test if we can import the app
echo "🧪 Testing Flask app import..."
cd /opt/python-app && sudo -u ec2-user /opt/python-venv/app/bin/python3 -c "import app; print('App import successful')"

# 5. Restart the service
echo "🔄 Restarting Python service..."
sudo systemctl restart python-app
sleep 3
sudo systemctl status python-app --no-pager

# 6. Test the application
echo "🧪 Testing application..."
sleep 2
curl -I http://localhost:5000/ 2>&1 | head -5

echo "✅ Python permissions fix complete!"
'''
success, output = client.run_command(script, timeout=180)
print(output)