#!/usr/bin/env python3
"""
Quick Python status check and fix
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'python-flask-api-v6'
    region = 'us-east-1'
    
    print(f"\n⚡ Quick Python Status Check for {instance_name}")
    print("=" * 60)
    
    client = LightsailBase(instance_name, region)
    
    # Quick status and fix
    quick_script = '''
echo "⚡ Quick Python status check..."

# 1. Check service status
if systemctl is-active --quiet python-app.service; then
    echo "✅ Python service is running"
else
    echo "❌ Python service not running - restarting..."
    sudo systemctl start python-app.service
    sleep 5
fi

# 2. Check if listening on port 5000
if sudo ss -tlnp | grep -q ":5000"; then
    echo "✅ App listening on port 5000"
else
    echo "❌ App not listening on port 5000"
fi

# 3. Quick external test
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "Testing external access to $PUBLIC_IP..."
if timeout 10 curl -s -f "http://$PUBLIC_IP/" > /tmp/test.html; then
    echo "✅ External access works!"
    echo "Response: $(head -1 /tmp/test.html)"
else
    echo "❌ External access failed"
    echo "Last nginx error:"
    sudo tail -1 /var/log/nginx/error.log 2>/dev/null || echo "No error log"
fi

echo "Status check complete."
'''
    
    success, output = client.run_command(quick_script, timeout=60)
    print(output)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())