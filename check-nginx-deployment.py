#!/usr/bin/env python3
"""
Quick check of nginx deployment status
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'nginx-static-demo-v6'
    region = 'us-east-1'
    
    print(f"\n⚡ Quick Nginx Status Check for {instance_name}")
    print("=" * 60)
    
    client = LightsailBase(instance_name, region)
    
    # Quick nginx status
    quick_script = '''
echo "⚡ Quick nginx status check..."

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "Public IP: $PUBLIC_IP"

# Test external access
if timeout 10 curl -s -f "http://$PUBLIC_IP/" > /tmp/test.html; then
    echo "✅ Nginx external access works!"
    echo "Response: $(head -1 /tmp/test.html)"
else
    echo "❌ Nginx external access failed"
fi

# Check nginx status
sudo systemctl status nginx --no-pager | head -3
'''
    
    success, output = client.run_command(quick_script, timeout=30)
    print(output)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())