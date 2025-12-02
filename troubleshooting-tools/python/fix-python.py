#!/usr/bin/env python3
"""
Comprehensive Python/Flask deployment fix script
Fixes permissions, restarts services, and validates deployment
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [python-app-demo]: ").strip() or 'python-app-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    reboot = input("Reboot instance after fix? (y/N): ").strip().lower() == 'y'
    
    print("\n🔧 Fixing Python/Flask Deployment Issues")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    fix_script = '''
set -e

echo "🔍 Finding Python application directory..."
APP_DIR=""
for dir in /opt/python-app /var/www/python-app /opt/app /var/www/app; do
    if [ -d "$dir" ] && [ -f "$dir/app.py" ]; then
        APP_DIR="$dir"
        echo "✅ Found application at: $APP_DIR"
        break
    fi
done

if [ -z "$APP_DIR" ]; then
    echo "❌ No Python application found in common locations"
    echo "Checked: /opt/python-app, /var/www/python-app, /opt/app, /var/www/app"
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
echo "🔧 4. Making app.py executable..."
sudo chmod 755 "$APP_DIR/app.py" 2>/dev/null || echo "app.py not found or already executable"

echo ""
echo "🔧 5. Checking if Gunicorn service exists..."
if sudo systemctl list-unit-files | grep -q gunicorn; then
    echo "Gunicorn service found, restarting..."
    sudo systemctl restart gunicorn
    echo "✅ Gunicorn restarted"
    
    echo ""
    echo "🔧 6. Checking Gunicorn status..."
    sudo systemctl status gunicorn --no-pager | head -15
else
    echo "⚠️ Gunicorn service not found, skipping restart"
fi

echo ""
echo "🔧 7. Reloading Nginx..."
sudo systemctl reload nginx 2>/dev/null || echo "Nginx not installed or not running"
echo "✅ Nginx reloaded"

echo ""
echo "🧪 Testing local access:"
sleep 2
curl -I http://localhost/ 2>&1 | head -10

echo ""
echo "✅ Fix complete!"
'''
    
    success, output = client.run_command(fix_script, timeout=120, max_retries=3)
    print(output)
    
    if not success:
        print("\n❌ Fix script failed")
        return 1
    
    print("\n✅ Python/Flask deployment fixed successfully")
    
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
