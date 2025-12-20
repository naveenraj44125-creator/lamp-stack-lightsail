#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workflows.lightsail_common import LightsailBase

client = LightsailBase('python-flask-api-v6', 'us-east-1')
script = '''
echo "=== Checking Python service logs ==="
sudo tail -50 /var/log/python-app/stderr.log 2>/dev/null || echo "No stderr.log"
echo ""
echo "=== Checking Python service output logs ==="
sudo tail -50 /var/log/python-app/output.log 2>/dev/null || echo "No output.log"
echo ""
echo "=== Checking if gunicorn is installed globally ==="
which gunicorn
/usr/local/bin/gunicorn --version 2>/dev/null || echo "Global gunicorn not found"
echo ""
echo "=== Checking pip3 packages ==="
pip3 list | grep gunicorn
echo ""
echo "=== Trying to create virtual environment manually ==="
cd /opt/python-venv && sudo rm -rf app && sudo python3 -m venv app
echo "Virtual environment created, checking:"
ls -la /opt/python-venv/app/bin/
'''
success, output = client.run_command(script, timeout=120)
print(output)