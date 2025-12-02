#!/usr/bin/env python3
"""
Comprehensive Nginx deployment fix script
Fixes permissions, ownership, and nginx configuration issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [nginx-static-demo]: ").strip() or 'nginx-static-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    reboot = input("Reboot instance after fix? (y/N): ").strip().lower() == 'y'
    
    print("\n🔧 Fixing Nginx Deployment Issues")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    fix_script = '''
set -e

echo "🔧 1. Fixing ownership..."
sudo chown -R www-data:www-data /var/www/html/
echo "✅ Set ownership to www-data:www-data"

echo ""
echo "🔧 2. Fixing directory permissions..."
sudo find /var/www/html -type d -exec chmod 755 {} \\;
echo "✅ Set directory permissions to 755"

echo ""
echo "🔧 3. Fixing file permissions..."
sudo find /var/www/html -type f -exec chmod 644 {} \\;
echo "✅ Set file permissions to 644"

echo ""
echo "🔧 4. Testing nginx configuration..."
sudo nginx -t

echo ""
echo "🔧 5. Reloading nginx..."
sudo systemctl reload nginx
echo "✅ Nginx reloaded"

echo ""
echo "📋 Current permissions:"
ls -la /var/www/html/ | head -15

echo ""
echo "🧪 Testing local access:"
curl -I http://localhost/ 2>&1 | head -10

echo ""
echo "✅ Fix complete!"
'''
    
    success, output = client.run_command(fix_script, timeout=120)
    print(output)
    
    if not success:
        print("\n❌ Fix script failed")
        return 1
    
    print("\n✅ Nginx deployment fixed successfully")
    
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
