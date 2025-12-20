#!/usr/bin/env python3
"""
Fix nginx deployment verification issue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'nginx-static-demo-v6'
    region = 'us-east-1'
    
    print(f"\n🔧 Fixing Nginx Verification Issue for {instance_name}")
    print("=" * 70)
    
    client = LightsailBase(instance_name, region)
    
    # Debug and fix nginx configuration
    fix_script = '''
echo "🔍 Debugging nginx configuration issue..."

# 1. Check current nginx configuration
echo "Current nginx configuration:"
sudo nginx -t

echo ""
echo "🔍 Checking nginx sites and configurations..."
echo "Main nginx.conf:"
sudo cat /etc/nginx/nginx.conf | grep -A 10 -B 5 "server {" || echo "No server block in main config"

echo ""
echo "Sites-enabled:"
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "No sites-enabled directory"

echo ""
echo "Sites-available:"
ls -la /etc/nginx/sites-available/ 2>/dev/null || echo "No sites-available directory"

echo ""
echo "Conf.d directory:"
ls -la /etc/nginx/conf.d/ 2>/dev/null || echo "No conf.d directory"

if [ -f /etc/nginx/conf.d/app.conf ]; then
    echo ""
    echo "App.conf content:"
    sudo cat /etc/nginx/conf.d/app.conf
else
    echo "❌ No app.conf found in conf.d"
fi

echo ""
echo "🔍 Checking what files are in the web directory..."
WEB_DIR="/var/www/html"
if [ -d "$WEB_DIR" ]; then
    echo "Files in $WEB_DIR:"
    ls -la "$WEB_DIR"
    
    echo ""
    echo "Index file content:"
    if [ -f "$WEB_DIR/index.html" ]; then
        head -10 "$WEB_DIR/index.html"
    else
        echo "❌ No index.html found"
    fi
else
    echo "❌ Web directory $WEB_DIR does not exist"
fi

echo ""
echo "🔧 Ensuring nginx is properly configured..."

# Remove any default site that might be interfering
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || echo "No default site to remove"

# Create a proper nginx configuration for static site
sudo tee /etc/nginx/conf.d/app.conf > /dev/null << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    root /var/www/html;
    index index.html index.htm;
    
    server_name _;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Main location block
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Handle static assets
    location ~* \\.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Security - deny access to hidden files
    location ~ /\\. {
        deny all;
    }
}
EOF

echo ""
echo "🔧 Removing any conflicting server blocks from main nginx.conf..."
# Backup original nginx.conf
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# Remove any server blocks from main nginx.conf
sudo sed -i '/server {/,/}/d' /etc/nginx/nginx.conf

echo ""
echo "🔧 Testing nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
    
    echo ""
    echo "🔄 Reloading nginx..."
    sudo systemctl reload nginx
    
    echo ""
    echo "🧪 Testing local access..."
    sleep 3
    if curl -s -f http://localhost/ > /tmp/test.html; then
        echo "✅ Local access works"
        echo "Response preview:"
        head -5 /tmp/test.html
    else
        echo "❌ Local access failed"
    fi
    
    echo ""
    echo "🧪 Testing external access..."
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    echo "Public IP: $PUBLIC_IP"
    
    if curl -s -f "http://$PUBLIC_IP/" > /tmp/external.html; then
        echo "✅ External access works"
        echo "Response preview:"
        head -5 /tmp/external.html
        
        # Check if it contains the expected content
        if grep -qi "nginx.*static\\|example\\|lightsail" /tmp/external.html; then
            echo "✅ Contains expected nginx static site content"
        else
            echo "⚠️ Content may not match expected patterns"
        fi
    else
        echo "❌ External access failed"
    fi
    
else
    echo "❌ Nginx configuration is invalid"
    sudo nginx -t
fi

echo ""
echo "✅ Nginx verification fix complete!"
'''
    
    success, output = client.run_command(fix_script, timeout=180)
    print(output)
    
    if success:
        print("\n✅ Nginx verification issue should be fixed!")
    else:
        print("\n❌ Failed to fix nginx verification issue")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())