#!/usr/bin/env python3
"""
Fix Nginx 403 permissions - run from local machine
"""

import sys
import os

# Add workflows directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'nginx-static-demo'
    region = 'us-east-1'
    
    print("=" * 80)
    print("🔧 FIXING NGINX 403 PERMISSIONS")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    # Fix script
    fix_script = '''
set -e
echo "🔧 Fixing Nginx 403 permissions..."

# Show current permissions
echo ""
echo "📋 Current permissions:"
ls -la /var/www/html/ | head -15

# Fix ownership
echo ""
echo "🔧 Setting ownership to www-data:www-data..."
sudo chown -R www-data:www-data /var/www/html/

# Fix directory permissions
echo "🔧 Setting directory permissions to 755..."
sudo find /var/www/html -type d -exec chmod 755 {} \\;

# Fix file permissions
echo "🔧 Setting file permissions to 644..."
sudo find /var/www/html -type f -exec chmod 644 {} \\;

# Show updated permissions
echo ""
echo "📋 Updated permissions:"
ls -la /var/www/html/ | head -15

# Test nginx config
echo ""
echo "🔍 Testing nginx configuration..."
sudo nginx -t

# Restart nginx
echo ""
echo "🔄 Restarting nginx..."
sudo systemctl restart nginx

# Check nginx status
echo ""
echo "📊 Nginx status:"
sudo systemctl status nginx --no-pager | head -10

# Test local access
echo ""
echo "🧪 Testing local access..."
curl -I http://localhost/

echo ""
echo "✅ Fix complete!"
'''
    
    print("\n🚀 Running fix script...")
    success, output = client.run_command(fix_script, timeout=120)
    print(output)
    
    if success:
        # Get public IP
        instance = client.lightsail.get_instance(instanceName=instance_name)['instance']
        ip = instance['publicIpAddress']
        
        print("\n" + "=" * 80)
        print("✅ FIX COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"🌐 Application URL: http://{ip}/")
        print("\n🧪 Testing external access...")
        
        import subprocess
        result = subprocess.run(f"curl -I http://{ip}/", shell=True, capture_output=True, text=True)
        if "200 OK" in result.stdout:
            print("✅ Site is accessible!")
        elif "403" in result.stdout:
            print("⚠️  Still getting 403 - may need additional troubleshooting")
        else:
            print(f"Response: {result.stdout[:200]}")
        
        return 0
    else:
        print("\n" + "=" * 80)
        print("❌ FIX FAILED")
        print("=" * 80)
        return 1

if __name__ == '__main__':
    sys.exit(main())
