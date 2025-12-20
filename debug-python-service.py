#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workflows.lightsail_common import LightsailBase

client = LightsailBase('python-flask-api-v6', 'us-east-1')
script = '''
echo "=== Checking Python application files ==="
ls -la /opt/python-app/
echo ""
echo "=== Checking Python service configuration ==="
sudo cat /etc/systemd/system/python-app.service
echo ""
echo "=== Checking nginx app.conf ==="
cat /etc/nginx/conf.d/app.conf
echo ""
echo "=== Checking Python virtual environment ==="
ls -la /opt/python-venv/app/
echo ""
echo "=== Trying to run the app manually ==="
cd /opt/python-app && /opt/python-venv/app/bin/python3 -c "import app; print('App import successful')" 2>&1 || echo "App import failed"
echo ""
echo "=== Checking Python path and modules ==="
cd /opt/python-app && /opt/python-venv/app/bin/python3 -c "import sys; print('Python path:'); [print(p) for p in sys.path]"
'''
success, output = client.run_command(script, timeout=60)
print(output)