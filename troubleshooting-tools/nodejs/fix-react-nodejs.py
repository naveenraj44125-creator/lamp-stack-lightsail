#!/usr/bin/env python3
"""
Automated fix script for React + Node.js deployment issues
Specifically designed for Instagram clone and similar React apps served by Node.js
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [react-app-instance-1]: ").strip() or 'react-app-instance-1'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print("\n🔧 Automated React + Node.js Deployment Fix")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    fix_script = '''
#!/bin/bash
set -e

echo "🔧 AUTOMATED REACT + NODE.JS DEPLOYMENT FIX"
echo "============================================"

# Find the application directory
APP_DIR=""
for dir in /opt/nodejs-app /var/www/html /opt/app /var/www/app; do
    if [ -d "$dir" ] && [ -f "$dir/package.json" ]; then
        APP_DIR="$dir"
        echo "✅ Found app directory: $APP_DIR"
        break
    fi
done

if [ -z "$APP_DIR" ]; then
    echo "❌ Could not find application directory with package.json"
    exit 1
fi

cd "$APP_DIR"
echo "📂 Working in: $(pwd)"

echo ""
echo "🔄 Step 1: Stopping existing processes"
echo "--------------------------------------"
pm2 stop all 2>/dev/null || echo "No PM2 processes to stop"
pm2 delete all 2>/dev/null || echo "No PM2 processes to delete"

echo ""
echo "📦 Step 2: Installing/updating dependencies"
echo "-------------------------------------------"
if [ -f "package-lock.json" ]; then
    echo "Using npm ci for clean install..."
    npm ci
else
    echo "Using npm install..."
    npm install
fi

echo ""
echo "🏗️  Step 3: Building React application"
echo "--------------------------------------"
echo "Cleaning previous build..."
rm -rf build/
echo "Building React app..."
npm run build

# Verify build was created
if [ -d "build" ] && [ -f "build/index.html" ]; then
    echo "✅ React build successful"
    echo "Build size: $(du -sh build/)"
    echo "Build contents:"
    ls -la build/ | head -10
else
    echo "❌ React build failed or incomplete"
    exit 1
fi

echo ""
echo "🖥️  Step 4: Starting Node.js server with PM2"
echo "--------------------------------------------"
if [ -f "server.js" ]; then
    echo "Starting server.js with PM2..."
    pm2 start server.js --name "react-app" --watch
    pm2 save
    echo "✅ Server started with PM2"
else
    echo "❌ server.js not found"
    exit 1
fi

echo ""
echo "🌐 Step 5: Configuring Nginx"
echo "----------------------------"
# Create Nginx configuration for Node.js proxy
sudo tee /etc/nginx/sites-available/nodejs-app > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Proxy all requests to Node.js server
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/nodejs-app /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration valid"
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded"
else
    echo "❌ Nginx configuration invalid"
    exit 1
fi

echo ""
echo "🔥 Step 6: Setting up firewall"
echo "------------------------------"
sudo ufw allow 22/tcp 2>/dev/null || true
sudo ufw allow 80/tcp 2>/dev/null || true
sudo ufw allow 443/tcp 2>/dev/null || true
echo "✅ Firewall configured"

echo ""
echo "🔍 Step 7: Verification"
echo "----------------------"
echo "PM2 status:"
pm2 status

echo ""
echo "Nginx status:"
sudo systemctl status nginx --no-pager

echo ""
echo "Testing local connectivity:"
sleep 5  # Give services time to start

echo "Node.js server (port 3000):"
curl -s -w "HTTP %{http_code}\n" http://localhost:3000/api/health | head -3

echo ""
echo "Nginx proxy (port 80):"
curl -s -w "HTTP %{http_code}\n" http://localhost:80/api/health | head -3

echo ""
echo "✅ AUTOMATED FIX COMPLETE!"
echo "=========================="
echo "🎯 Next steps:"
echo "1. Test external access: http://$(curl -s ifconfig.me)/"
echo "2. Check PM2 logs: pm2 logs"
echo "3. Check Nginx logs: sudo tail -f /var/log/nginx/error.log"
'''
    
    print("\n🚀 Running automated fix script...")
    print("⚠️  This will:")
    print("   • Stop existing PM2 processes")
    print("   • Reinstall npm dependencies")
    print("   • Rebuild React application")
    print("   • Restart Node.js server with PM2")
    print("   • Reconfigure Nginx proxy")
    
    confirm = input("\nProceed with automated fix? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Fix cancelled")
        return 1
    
    success, output = client.run_command(fix_script, timeout=300)
    print(output)
    
    if success:
        print("\n" + "="*80)
        print("🎉 AUTOMATED FIX COMPLETED SUCCESSFULLY!")
        print("="*80)
        
        # Get instance IP for testing
        try:
            instance_info = client.lightsail.get_instance(instanceName=instance_name)
            ip_address = instance_info['instance']['publicIpAddress']
            print(f"\n🌐 Test your application:")
            print(f"   Main App: http://{ip_address}/")
            print(f"   Health Check: http://{ip_address}/api/health")
            print(f"   Status: http://{ip_address}/api/status")
        except Exception as e:
            print(f"❌ Could not get instance IP: {e}")
        
        print(f"\n📊 Monitoring commands:")
        print(f"   PM2 status: pm2 status")
        print(f"   PM2 logs: pm2 logs")
        print(f"   Nginx logs: sudo tail -f /var/log/nginx/error.log")
        
    else:
        print("\n❌ Automated fix failed")
        print("💡 Try running the debug script first: python3 debug-react-nodejs.py")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())