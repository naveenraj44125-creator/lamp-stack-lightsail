#!/usr/bin/env python3
"""
Test Python external connectivity with known IP
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'python-flask-api-v6'
    region = 'us-east-1'
    
    print(f"\n🧪 Testing Python External Connectivity")
    print("=" * 50)
    
    client = LightsailBase(instance_name, region)
    
    # Get the public IP from the client connection info
    public_ip = client.public_ip
    print(f"Testing with IP: {public_ip}")
    
    # Test external connectivity
    test_script = f'''
echo "🧪 Testing external connectivity to {public_ip}..."

# Test HTTP access
if curl -s -f "http://{public_ip}/" > /tmp/external-test.html; then
    echo "✅ External HTTP access successful!"
    echo "Response preview:"
    head -3 /tmp/external-test.html
    
    # Test health endpoint
    if curl -s -f "http://{public_ip}/api/health" > /tmp/health-external.json; then
        echo "✅ External health endpoint working:"
        cat /tmp/health-external.json
    else
        echo "⚠️ Health endpoint not accessible externally"
    fi
else
    echo "❌ External HTTP access failed"
    echo "Checking nginx status and logs..."
    
    # Check nginx status
    sudo systemctl status nginx --no-pager | head -5
    
    echo ""
    echo "Nginx error log:"
    sudo tail -5 /var/log/nginx/error.log 2>/dev/null || echo "No error log"
    
    echo ""
    echo "Testing direct Flask access (port 5000):"
    if curl -s -f "http://{public_ip}:5000/" > /tmp/direct-test.html; then
        echo "✅ Direct Flask access works - nginx proxy issue"
        echo "Response:"
        head -2 /tmp/direct-test.html
    else
        echo "❌ Direct Flask access also fails"
    fi
fi
'''
    
    success, output = client.run_command(test_script, timeout=60)
    print(output)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())