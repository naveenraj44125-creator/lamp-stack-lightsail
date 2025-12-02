#!/usr/bin/env python3
"""
Comprehensive Node.js deployment fix script
Fixes permissions, restarts PM2, and validates deployment
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [nodejs-app-demo]: ").strip() or 'nodejs-app-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    reboot = input("Reboot instance after fix? (y/N): ").strip().lower() == 'y'
    
    print("\n🔧 Fixing Node.js Deployment Issues")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    fix_script = '''
set -e

echo "🔍 Finding Node.js application directory..."
APP_DIR=""
for dir in /opt/nodejs-app /var/www/nodejs-app /opt/app /var/www/app; do
    if [ -d "$dir" ] && [ -f "$dir/package.json" ]; then
        APP_DIR="$dir"
        echo "✅ Found application at: $APP_DIR"
        break
    fi
done

if [ -z "$APP_DIR" ]; then
    echo "❌ No Node.js application found in common locations"
    echo "Checked: /opt/nodejs-app, /var/www/nodejs-app, /opt/app, /var/www/app"
    exit 1
fi

echo ""
echo "🔧 1. Fixing application directory ownership..."
sudo chown -R ubuntu:ubuntu "$APP_DIR"
echo "✅ Ownership fixed for $APP_DIR"

echo ""
echo "🔧 2. Fixing directory permissions..."
sudo find "$APP_DIR" -type d -exec chmod 755 {} \\;
echo "✅ Directory permissions fixed"

echo ""
echo "🔧 3. Fixing file permissions..."
sudo find "$APP_DIR" -type f -exec chmod 644 {} \\;
echo "✅ File permissions fixed"

echo ""
echo "🔧 4. Making app.js executable..."
sudo chmod 755 "$APP_DIR/app.js" 2>/dev/null || echo "app.js not found or already executable"

echo ""
echo "🔧 5. Checking if PM2 has any apps..."
PM2_COUNT=$(pm2 list | grep -c "online\\|stopped\\|errored" || echo "0")
if [ "$PM2_COUNT" -gt 0 ]; then
    echo "Found $PM2_COUNT PM2 app(s), restarting..."
    pm2 restart all
    echo "✅ PM2 restarted"
else
    echo "No PM2 apps found, starting application..."
    cd "$APP_DIR"
    pm2 start app.js --name nodejs-app
    pm2 save
    echo "✅ Application started with PM2"
fi

echo ""
echo "🔧 6. Checking PM2 status..."
pm2 status

echo ""
echo "🔧 7. Saving PM2 configuration..."
pm2 save
echo "✅ PM2 configuration saved"

echo ""
echo "🔧 8. Reloading Nginx..."
sudo systemctl reload nginx 2>/dev/null || echo "Nginx not installed or not running"
echo "✅ Nginx reloaded"

echo ""
echo "🧪 Testing local access:"
sleep 2
curl -I http://localhost/ 2>&1 | head -10

echo ""
echo "✅ Fix complete!"
'''
    
    success, output = client.run_command(fix_script, timeout=120)
    print(output)
    
    if not success:
        print("\n❌ Fix script failed")
        return 1
    
    print("\n✅ Node.js deployment fixed successfully")
    
    if reboot:
        print("\n🔄 Rebooting instance...")
        import boto3
        lightsail = boto3.client('lightsail', region_name=region)
        try:
            lightsail.reboot_instance(instanceName=instance_name)
            print(f"✅ Reboot initiated for {instance_name}")
            print("⏳ Instance will be back online in ~1-2 minutes")
        except Exception as e:
            print(f"❌ Failed to reboot: {str(e)}")
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
