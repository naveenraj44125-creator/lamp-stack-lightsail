#!/bin/bash
# Quick fix for nginx permissions using AWS CLI

INSTANCE_NAME="${1:-nginx-static-demo}"
REGION="${2:-us-east-1}"

echo "🔧 Quick Nginx Permission Fix"
echo "Instance: $INSTANCE_NAME"
echo "Region: $REGION"
echo ""

# Get instance IP
IP=$(aws lightsail get-instance --instance-name "$INSTANCE_NAME" --region "$REGION" --query 'instance.publicIpAddress' --output text)
echo "✅ Instance IP: $IP"
echo ""

# Create fix script
cat > /tmp/fix-nginx.sh << 'FIXSCRIPT'
#!/bin/bash
set -x

echo "🔧 Fixing nginx permissions..."

# Fix ownership
sudo chown -R www-data:www-data /var/www/html/
echo "✅ Set ownership to www-data:www-data"

# Fix directory permissions
sudo find /var/www/html -type d -exec chmod 755 {} \;
echo "✅ Set directory permissions to 755"

# Fix file permissions
sudo find /var/www/html -type f -exec chmod 644 {} \;
echo "✅ Set file permissions to 644"

# List files
echo ""
echo "📋 Files in /var/www/html:"
ls -la /var/www/html/

# Test nginx config
echo ""
echo "🔍 Testing nginx config..."
sudo nginx -t

# Restart nginx
echo ""
echo "🔄 Restarting nginx..."
sudo systemctl restart nginx
sudo systemctl status nginx --no-pager

# Test local access
echo ""
echo "🌐 Testing local access..."
curl -I http://localhost/

echo ""
echo "✅ Fix complete!"
FIXSCRIPT

chmod +x /tmp/fix-nginx.sh

echo "📤 Uploading fix script to instance..."
aws lightsail put-instance-public-ports \
  --instance-name "$INSTANCE_NAME" \
  --region "$REGION" \
  --port-infos fromPort=22,toPort=22,protocol=tcp fromPort=80,toPort=80,protocol=tcp fromPort=443,toPort=443,protocol=tcp \
  > /dev/null 2>&1

echo ""
echo "⚠️  Manual Steps Required:"
echo ""
echo "1. Open Lightsail console: https://lightsail.aws.amazon.com/ls/webapp/home/instances"
echo "2. Click on '$INSTANCE_NAME'"
echo "3. Click 'Connect using SSH' button"
echo "4. Run these commands:"
echo ""
echo "   sudo chown -R www-data:www-data /var/www/html/"
echo "   sudo find /var/www/html -type d -exec chmod 755 {} \\;"
echo "   sudo find /var/www/html -type f -exec chmod 644 {} \\;"
echo "   sudo systemctl restart nginx"
echo ""
echo "5. Test: curl http://localhost/"
echo "6. Test externally: http://$IP/"
echo ""
