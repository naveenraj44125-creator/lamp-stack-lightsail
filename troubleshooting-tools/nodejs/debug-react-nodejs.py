#!/usr/bin/env python3
"""
Comprehensive React + Node.js deployment debug script
Specifically designed for React apps served by Node.js (like Instagram clone)
Checks React build, Node.js server, PM2, Nginx proxy, and file structure
"""

import sys
import os
import json
import requests
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def test_endpoints(ip_address):
    """Test various endpoints to diagnose issues"""
    print("\n🌐 Testing External Endpoints")
    print("-" * 50)
    
    endpoints = [
        ("Main App", f"http://{ip_address}/"),
        ("Health Check", f"http://{ip_address}/api/health"),
        ("Status Check", f"http://{ip_address}/api/status"),
        ("Posts API", f"http://{ip_address}/api/posts"),
    ]
    
    for name, url in endpoints:
        try:
            print(f"📍 Testing {name}: {url}")
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                content = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"   Content: {content}")
            else:
                print(f"   Error: {response.text[:100]}")
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
        print()

def main():
    instance_name = input("Instance name [react-app-instance-1]: ").strip() or 'react-app-instance-1'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print("\n🔍 Debugging React + Node.js Deployment (Instagram Clone)")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    # Get instance IP for external testing
    try:
        instance_info = client.lightsail.get_instance(instanceName=instance_name)
        ip_address = instance_info['instance']['publicIpAddress']
        print(f"📍 Instance IP: {ip_address}")
    except Exception as e:
        print(f"❌ Could not get instance IP: {e}")
        ip_address = None
    
    debug_script = '''
echo "🔍 REACT + NODE.JS DEPLOYMENT DIAGNOSTICS"
echo "=========================================="

echo ""
echo "📋 1. SYSTEM INFORMATION"
echo "------------------------"
echo "OS Version:"
cat /etc/os-release | grep PRETTY_NAME
echo ""
echo "Current User: $(whoami)"
echo "Current Directory: $(pwd)"
echo "Date: $(date)"

echo ""
echo "📋 2. NODE.JS ENVIRONMENT"
echo "-------------------------"
echo "Node.js version:"
node --version 2>&1 || echo "❌ Node.js not found"
echo ""
echo "npm version:"
npm --version 2>&1 || echo "❌ npm not found"
echo ""
echo "Global npm packages:"
npm list -g --depth=0 2>/dev/null | head -10

echo ""
echo "📋 3. APPLICATION DIRECTORY STRUCTURE"
echo "-------------------------------------"
echo "Checking common app locations:"
for dir in /opt/nodejs-app /var/www/html /opt/app /var/www/app; do
    if [ -d "$dir" ]; then
        echo "✅ Found: $dir"
        echo "Contents:"
        ls -la "$dir" | head -10
        echo ""
        
        # Check for package.json
        if [ -f "$dir/package.json" ]; then
            echo "📦 package.json found:"
            cat "$dir/package.json" | head -20
            echo ""
        fi
        
        # Check for React build
        if [ -d "$dir/build" ]; then
            echo "🏗️  React build directory found:"
            ls -la "$dir/build" | head -10
            echo ""
            if [ -f "$dir/build/index.html" ]; then
                echo "✅ index.html exists in build"
                echo "Size: $(du -sh $dir/build/index.html)"
            else
                echo "❌ index.html missing in build"
            fi
        else
            echo "❌ No build directory found"
        fi
        
        # Check for server.js
        if [ -f "$dir/server.js" ]; then
            echo "🖥️  server.js found:"
            head -20 "$dir/server.js"
            echo ""
        fi
        
        break
    else
        echo "❌ Not found: $dir"
    fi
done

echo ""
echo "📋 4. PM2 PROCESS MANAGEMENT"
echo "----------------------------"
echo "PM2 status:"
pm2 status 2>&1 || echo "❌ PM2 not available or no processes"
echo ""
echo "PM2 logs (last 50 lines):"
pm2 logs --lines 50 --nostream 2>&1 || echo "❌ No PM2 logs available"

echo ""
echo "📋 5. NODE.JS PROCESSES"
echo "-----------------------"
echo "Running Node.js processes:"
ps aux | grep node | grep -v grep || echo "❌ No Node.js processes found"

echo ""
echo "📋 6. NGINX CONFIGURATION"
echo "-------------------------"
echo "Nginx status:"
sudo systemctl status nginx --no-pager 2>&1
echo ""
echo "Nginx configuration files:"
ls -la /etc/nginx/sites-enabled/
echo ""
echo "Main Nginx config:"
cat /etc/nginx/sites-enabled/default 2>/dev/null || cat /etc/nginx/sites-enabled/app 2>/dev/null || echo "❌ No Nginx config found"

echo ""
echo "📋 7. NGINX LOGS"
echo "----------------"
echo "Nginx access log (last 20 lines):"
sudo tail -20 /var/log/nginx/access.log 2>/dev/null || echo "❌ No access log"
echo ""
echo "Nginx error log (last 20 lines):"
sudo tail -20 /var/log/nginx/error.log 2>/dev/null || echo "❌ No error log"

echo ""
echo "📋 8. NETWORK & PORTS"
echo "---------------------"
echo "Listening ports:"
sudo netstat -tlnp | grep -E ':(80|443|3000|8080)' || echo "❌ No web ports listening"
echo ""
echo "Firewall status:"
sudo ufw status 2>/dev/null || echo "❌ UFW not available"

echo ""
echo "📋 9. LOCAL CONNECTIVITY TESTS"
echo "------------------------------"
echo "Testing localhost:3000 (Node.js server):"
curl -I http://localhost:3000/ 2>&1 | head -5
echo ""
echo "Testing localhost:80 (Nginx):"
curl -I http://localhost:80/ 2>&1 | head -5
echo ""
echo "Testing Node.js health endpoint:"
curl -s http://localhost:3000/api/health 2>&1 | head -5

echo ""
echo "📋 10. DISK SPACE & PERMISSIONS"
echo "-------------------------------"
echo "Disk usage:"
df -h | grep -E '(Filesystem|/dev/)'
echo ""
echo "App directory permissions:"
for dir in /opt/nodejs-app /var/www/html; do
    if [ -d "$dir" ]; then
        ls -ld "$dir"
        ls -la "$dir" | head -5
        break
    fi
done

echo ""
echo "📋 11. RECENT SYSTEM LOGS"
echo "-------------------------"
echo "Recent deployment-related logs:"
sudo journalctl -u nginx --since "1 hour ago" --no-pager | tail -10 2>/dev/null || echo "❌ No recent Nginx logs"

echo ""
echo "🔍 DIAGNOSIS COMPLETE"
echo "===================="
'''
    
    print("\n🚀 Running comprehensive diagnostics...")
    success, output = client.run_command(debug_script, timeout=180)
    print(output)
    
    if not success:
        print("\n❌ Debug script failed")
        return 1
    
    # Test external endpoints if we have the IP
    if ip_address:
        test_endpoints(ip_address)
    
    print("\n" + "="*80)
    print("🎯 TROUBLESHOOTING RECOMMENDATIONS")
    print("="*80)
    
    # Analyze output for common issues
    if "❌ No build directory found" in output:
        print("🔧 ISSUE: React build missing")
        print("   Solution: Run 'npm run build' in the app directory")
        print("   Command: cd /opt/nodejs-app && npm run build")
    
    if "❌ No Node.js processes found" in output:
        print("🔧 ISSUE: Node.js server not running")
        print("   Solution: Start the server with PM2")
        print("   Command: cd /opt/nodejs-app && pm2 start server.js --name react-app")
    
    if "❌ No web ports listening" in output:
        print("🔧 ISSUE: No web services listening")
        print("   Solution: Check Nginx and Node.js server status")
        print("   Commands: sudo systemctl restart nginx && pm2 restart all")
    
    print("\n✅ Comprehensive diagnostics complete!")
    print(f"📊 Check the output above for specific issues and solutions")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())