#!/usr/bin/env python3
"""
Test script specifically for Instagram clone deployment
Uses hardcoded values for quick testing
"""

import sys
import os
import requests
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'instagram-clone-instance-1'
    region = 'us-east-1'
    
    print(f"\n⚡ Testing Instagram Clone Deployment")
    print(f"📍 Instance: {instance_name}")
    print(f"🌍 Region: {region}")
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
    
    # Test external endpoints
    print(f"\n🌐 External Connectivity Test")
    print("-" * 30)
    
    endpoints = [
        ("Main App", f"http://{ip_address}/"),
        ("Health API", f"http://{ip_address}/api/health"),
        ("Status API", f"http://{ip_address}/api/status"),
        ("Posts API", f"http://{ip_address}/api/posts"),
    ]
    
    results = {}
    for name, url in endpoints:
        try:
            print(f"Testing {name}...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK (200)")
                if 'api' in url:
                    # Show API response for debugging
                    try:
                        data = response.json()
                        if 'build_exists' in data:
                            print(f"   Build exists: {data.get('build_exists', 'unknown')}")
                        if 'build_path' in data:
                            print(f"   Build path: {data.get('build_path', 'unknown')}")
                    except:
                        pass
                results[name] = 'OK'
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results[name] = f'HTTP {response.status_code}'
        except Exception as e:
            print(f"❌ {name}: Failed ({str(e)})")
            results[name] = 'Failed'
    
    # Run quick server diagnostics
    print(f"\n🔍 Server Diagnostics")
    print("-" * 20)
    
    quick_check_script = '''
# Check if app directory exists and has build
APP_DIR=""
for dir in /opt/nodejs-app /var/www/html /opt/app; do
    if [ -d "$dir" ]; then
        APP_DIR="$dir"
        break
    fi
done

if [ -n "$APP_DIR" ]; then
    echo "App directory: $APP_DIR"
    cd "$APP_DIR"
    
    if [ -d "build" ] && [ -f "build/index.html" ]; then
        echo "React build: EXISTS"
        echo "Build size: $(du -sh build/ 2>/dev/null || echo 'unknown')"
    else
        echo "React build: MISSING"
    fi
    
    if [ -f "server.js" ]; then
        echo "Server.js: EXISTS"
    else
        echo "Server.js: MISSING"
    fi
else
    echo "App directory: NOT FOUND"
fi

# Check processes
if pgrep -f "node.*server.js" >/dev/null; then
    echo "Node.js server: RUNNING"
else
    echo "Node.js server: NOT RUNNING"
fi

if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "Nginx: RUNNING"
else
    echo "Nginx: NOT RUNNING"
fi

# Check ports
if netstat -tlnp 2>/dev/null | grep -q ":3000"; then
    echo "Port 3000: LISTENING"
else
    echo "Port 3000: NOT LISTENING"
fi

if netstat -tlnp 2>/dev/null | grep -q ":80"; then
    echo "Port 80: LISTENING"
else
    echo "Port 80: NOT LISTENING"
fi
'''
    
    success, output = client.run_command(quick_check_script, timeout=60)
    if success:
        print(output)
    else:
        print("❌ Could not run server diagnostics")
    
    # Summary
    print(f"\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    
    working_count = sum(1 for status in results.values() if status == 'OK')
    total_count = len(results)
    
    if working_count == total_count:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print(f"🌐 Instagram Clone is live at: http://{ip_address}/")
    else:
        print(f"⚠️  ISSUES DETECTED ({working_count}/{total_count} endpoints working)")
        print("\n💡 Recommended actions:")
        
        if results.get('Health API') == 'OK' and results.get('Main App') != 'OK':
            print("   • Server is running but React build may be missing")
            print("   • Run: python3 fix-react-nodejs.py")
        elif results.get('Health API') != 'OK':
            print("   • Node.js server may not be running")
            print("   • Run: python3 fix-react-nodejs.py")
        else:
            print("   • Run: python3 debug-react-nodejs.py (detailed diagnosis)")
    
    return 0 if working_count == total_count else 1

if __name__ == '__main__':
    sys.exit(main())