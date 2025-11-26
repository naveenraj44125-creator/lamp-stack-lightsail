#!/bin/bash
# Fix Nginx 403 permissions
# Run this script ON the Lightsail instance

set -e

echo "🔧 Fixing Nginx 403 Permissions"
echo "=================================="

# Check if running on server
if [ ! -d "/var/www/html" ]; then
    echo "❌ /var/www/html not found"
    echo "⚠️  This script should be run on the Lightsail instance"
    exit 1
fi

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
sudo find /var/www/html -type d -exec chmod 755 {} \;

# Fix file permissions
echo "🔧 Setting file permissions to 644..."
sudo find /var/www/html -type f -exec chmod 644 {} \;

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
echo ""
echo "🌐 Test from outside:"
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "   curl http://$PUBLIC_IP/"
echo "   or visit: http://$PUBLIC_IP/"
