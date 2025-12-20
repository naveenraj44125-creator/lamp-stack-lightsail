#!/usr/bin/env python3
"""
Quick diagnostic script for React + Node.js deployments
Provides immediate status check and common issue identification
"""

import sys
import os
import requests
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [react-app-instance-1]: ").strip() or 'react-app-instance-1'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print("\n⚡ Quick React + Node.js Deployment Check")
    print("=" * 50)
    
    client = LightsailBase(instance_name, region)
    
    # Get instance IP
    try:
        instance_info = client.lightsail.get_instance(instanceName=instance_name)
        ip_address = instance_info['instance']['publicIpAddress']
        print(f"📍 Instance IP: {ip_address}")
    except Exception as e:
        print(f"❌ Could not get instance IP: {e}")
        return 1
    
    quick_check_script = '''
echo "⚡ QUICK STATUS CHECK"
echo "===================="

# Check if app directory exists
APP_DIR=""
for dir in /opt/nodejs-app /var/www/html /opt/app; do
    if [ -d "$dir" ]; then
        APP_DIR="$dir"
        break
    fi
done

if [ -n "$APP_DIR" ]; then
    echo "✅ App directory: $APP_DIR"
    cd "$APP_DIR"
    
    # Check React build
    if [ -d "build" ] && [ -f "build/index.html" ]; then
        echo "✅ React build exists"
    else
        echo "❌ React build missing"
    fi
    
    # Check server.js
    if [ -f "server.js" ]; then
        echo "✅ server.js exists"
    else
        echo "❌ server.js missing"
    fi
else
    echo "❌ App directory not found"
fi

# Check Node.js
if command -v node >/dev/null 2>&1; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js not installed"
fi

# Check PM2
if command -v pm2 >/dev/null 2>&1; then
    PROCESSES=$(pm2 list | grep -c "online" 2>/dev/null || echo "0")
    if [ "$PROCESSES" -gt 0 ]; then
        echo "✅ PM2: $PROCESSES process(es) running"
    else
        echo "❌ PM2: No processes running"
    fi
else
    echo "❌ PM2 not installed"
fi

# Check Nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: Running"
else
    echo "❌ Nginx: Not running"
fi

# Check ports
if netstat -tlnp 2>/dev/null | grep -q ":3000"; then
    echo "✅ Port 3000: Node.js listening"
else
    echo "❌ Port 3000: Nothing listening"
fi

if netstat -tlnp 2>/dev/null | grep -q ":80"; then
    echo "✅ Port 80: Web server listening"
else
    echo "❌ Port 80: Nothing listening"
fi

# Quick connectivity test
echo ""
echo "🔗 Local connectivity:"
curl -s -w "Status: %{http_code}\n" -o /dev/null http://localhost:3000/api/health 2>/dev/null || echo "❌ Node.js server unreachable"
curl -s -w "Status: %{http_code}\n" -o /dev/null http://localhost:80/ 2>/dev/null || echo "❌ Web server unreachable"
'''
    
    print("\n🚀 Running quick check...")
    success, output = client.run_command(quick_check_script, timeout=60)
    print(output)
    
    # Test external endpoints
    print("\n🌐 External Connectivity Test")
    print("-" * 30)
    
    endpoints = [
        ("Main App", f"http://{ip_address}/"),
        ("Health API", f"http://{ip_address}/api/health"),
    ]
    
    all_working = True
    for name, url in endpoints:
        try:
            print(f"Testing {name}...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK (200)")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"❌ {name}: Failed ({str(e)})")
            all_working = False
    
    print("\n" + "="*50)
    if all_working:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print(f"🌐 Your app is live at: http://{ip_address}/")
    else:
        print("⚠️  ISSUES DETECTED")
        print("💡 Recommended actions:")
        
        if "❌ React build missing" in output:
            print("   1. Run: python3 fix-react-nodejs.py")
        elif "❌ PM2: No processes running" in output:
            print("   1. Run: python3 fix-react-nodejs.py")
        elif "❌ Nginx: Not running" in output:
            print("   1. Run: python3 fix-react-nodejs.py")
        else:
            print("   1. Run: python3 debug-react-nodejs.py (detailed diagnosis)")
            print("   2. Run: python3 fix-react-nodejs.py (automated fix)")
    
    return 0 if all_working else 1

if __name__ == '__main__':
    sys.exit(main())