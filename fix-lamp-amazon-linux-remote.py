#!/usr/bin/env python3
"""
Fix LAMP Stack deployment issues on Amazon Linux via SSH
This script addresses the specific issues found in the debug output
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = "amazon-linux-test-v7-20241220"
    region = "us-east-1"
    
    print("\n🔧 Fixing LAMP Stack Deployment Issues on Amazon Linux")
    print("=" * 60)
    print(f"Instance: {instance_name}")
    print(f"Region: {region}")
    print("=" * 60)
    
    client = LightsailBase(instance_name, region)
    
    # Comprehensive fix script for Amazon Linux
    fix_script = '''
set -e

echo "🔧 Step 1: Installing missing PHP..."
sudo yum install -y php php-mysqlnd php-pgsql php-curl php-mbstring php-xml php-zip
echo "✅ PHP installed"

echo ""
echo "🔧 Step 2: Fixing file ownership (using apache user for Amazon Linux)..."
sudo chown -R apache:apache /var/www/html/
echo "✅ Set ownership to apache:apache"

echo ""
echo "🔧 Step 3: Fixing directory permissions..."
sudo find /var/www/html -type d -exec chmod 755 {} \\;
echo "✅ Set directory permissions to 755"

echo ""
echo "🔧 Step 4: Fixing file permissions..."
sudo find /var/www/html -type f -exec chmod 644 {} \\;
echo "✅ Set file permissions to 644"

echo ""
echo "🔧 Step 5: Creating a simple index.html for testing..."
cat > /tmp/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>LAMP Stack - Apache Working</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .success { color: #28a745; font-size: 24px; margin-bottom: 20px; }
        .info { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="success">✅ LAMP Stack Deployment Successful!</h1>
        <div class="info">
            <p><strong>Server:</strong> Apache (httpd) on Amazon Linux 2023</p>
            <p><strong>Instance:</strong> amazon-linux-test-v7-20241220</p>
            <p><strong>IP Address:</strong> 54.175.20.108</p>
            <p><strong>Document Root:</strong> /var/www/html</p>
            <p><strong>Status:</strong> Web server is running and accessible</p>
        </div>
        <p>Your LAMP stack has been deployed successfully on Amazon Linux 2023. Apache is now serving content correctly.</p>
        <p><strong>Available Files:</strong></p>
        <ul>
            <li><a href="index.php">index.php</a> - Main LAMP application</li>
            <li><a href="bucket-demo.php">bucket-demo.php</a> - S3 bucket demo</li>
            <li><a href="bucket-manager.php">bucket-manager.php</a> - Bucket manager</li>
        </ul>
    </div>
</body>
</html>
EOF

sudo mv /tmp/index.html /var/www/html/index.html
sudo chown apache:apache /var/www/html/index.html
sudo chmod 644 /var/www/html/index.html
echo "✅ Created index.html"

echo ""
echo "🔧 Step 6: Testing Apache configuration..."
sudo httpd -t
echo "✅ Apache configuration is valid"

echo ""
echo "🔧 Step 7: Starting Apache service..."
sudo systemctl start httpd
echo "✅ Apache started"

echo ""
echo "🔧 Step 8: Enabling Apache to start on boot..."
sudo systemctl enable httpd
echo "✅ Apache enabled for auto-start"

echo ""
echo "🔧 Step 9: Checking firewall..."
if sudo systemctl is-active firewalld >/dev/null 2>&1; then
    echo "Firewall is active, opening HTTP port..."
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --reload
    echo "✅ HTTP port opened in firewall"
else
    echo "✅ Firewall is not active, no changes needed"
fi

echo ""
echo "📋 Step 10: Verifying file permissions:"
ls -la /var/www/html/ | head -10

echo ""
echo "🧪 Step 11: Testing local HTTP access:"
curl -I http://localhost/ 2>&1 | head -5

echo ""
echo "🧪 Step 12: Testing PHP functionality:"
php -r "echo 'PHP Version: ' . phpversion() . PHP_EOL;"

echo ""
echo "📊 Step 13: Final service status:"
sudo systemctl status httpd --no-pager -l | head -10

echo ""
echo "🎉 LAMP Stack fix completed!"
echo "🌐 Test external access: http://54.175.20.108/"
'''
    
    print("🚀 Executing comprehensive LAMP fix...")
    success, output = client.run_command(fix_script, timeout=300)
    print(output)
    
    if success:
        print("\n✅ LAMP Stack fix completed successfully!")
        print("🌐 Testing external access...")
        
        # Test the endpoint
        import requests
        import time
        
        # Wait a moment for services to fully start
        time.sleep(5)
        
        try:
            response = requests.get("http://54.175.20.108/", timeout=15)
            if response.status_code == 200:
                print("✅ External HTTP access is working!")
                print(f"   Status: {response.status_code}")
                print(f"   Content preview: {response.text[:100]}...")
                return 0
            else:
                print(f"⚠️  External access returned status: {response.status_code}")
                return 1
        except Exception as e:
            print(f"❌ External access test failed: {str(e)}")
            print("💡 The fix may have worked, but external access might need a moment to propagate")
            return 1
    else:
        print("\n❌ LAMP Stack fix failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())