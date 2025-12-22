#!/usr/bin/env python3
"""
Fix MySQL access for Reddit Clone app
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = 'reddit-clone-app'
    region = 'us-east-1'
    
    print("\n🔧 Fixing MySQL for Reddit Clone App")
    print("=" * 50)
    
    client = LightsailBase(instance_name, region)
    
    # Get instance IP
    try:
        instance_info = client.lightsail.get_instance(instanceName=instance_name)
        ip_address = instance_info['instance']['publicIpAddress']
        print(f"📍 Instance IP: {ip_address}")
    except Exception as e:
        print(f"❌ Could not get instance: {e}")
        return 1
    
    # Fix MySQL - reset root password and create database/user
    fix_mysql_script = '''
echo "🔧 Fixing MySQL access..."

# First, check if MySQL is running
sudo systemctl status mysql 2>&1 | head -5 || sudo systemctl status mariadb 2>&1 | head -5

# Stop MySQL
echo "Stopping MySQL..."
sudo systemctl stop mysql 2>/dev/null || sudo systemctl stop mariadb 2>/dev/null

# Start MySQL in safe mode to reset root password
echo "Starting MySQL in safe mode..."
sudo mkdir -p /var/run/mysqld
sudo chown mysql:mysql /var/run/mysqld
sudo mysqld_safe --skip-grant-tables &
sleep 5

# Reset root password and create user
echo "Resetting MySQL root and creating app_user..."
mysql -u root << 'EOF'
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root_password_123';
CREATE DATABASE IF NOT EXISTS reddit_clone;
DROP USER IF EXISTS 'app_user'@'localhost';
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'CHANGE_ME_secure_password_123';
GRANT ALL PRIVILEGES ON reddit_clone.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
SELECT 'MySQL configured successfully' as status;
EOF

# Kill safe mode MySQL
echo "Stopping safe mode MySQL..."
sudo pkill -f mysqld_safe 2>/dev/null || true
sudo pkill -f mysqld 2>/dev/null || true
sleep 3

# Start MySQL normally
echo "Starting MySQL normally..."
sudo systemctl start mysql 2>/dev/null || sudo systemctl start mariadb 2>/dev/null
sleep 3

# Test the connection
echo "🔍 Testing MySQL connection..."
mysql -u app_user -p'CHANGE_ME_secure_password_123' -e "USE reddit_clone; SELECT 'Connection successful' as status;" 2>&1

# Check .env file and update password if needed
echo ""
echo "🔍 Checking .env configuration..."
cat /opt/nodejs-app/.env 2>/dev/null || echo "No .env file found"
'''
    
    print("\n🚀 Running MySQL fix...")
    success, output = client.run_command(fix_mysql_script, timeout=120)
    print(output)
    
    if not success:
        print("❌ MySQL fix failed")
        return 1
    
    # Now install PM2 and restart the Node.js app
    restart_app_script = '''
echo "🔄 Setting up Node.js app..."

cd /opt/nodejs-app

# Install PM2 globally if not installed
if ! command -v pm2 &> /dev/null; then
    echo "📦 Installing PM2..."
    sudo npm install -g pm2 2>&1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install 2>&1
fi

# Stop any existing PM2 processes
pm2 delete all 2>/dev/null || true

# Start the app with PM2
echo "🚀 Starting app with PM2..."
pm2 start server.js --name reddit-clone 2>&1

# Wait a moment
sleep 3

# Check PM2 status
echo ""
echo "📊 PM2 Status:"
pm2 list

# Save PM2 process list
pm2 save 2>/dev/null || true

# Check if app is responding
echo ""
echo "🔍 Testing local endpoints..."
curl -s http://localhost:3000/api/health 2>&1 || echo "Health endpoint not responding"

# Check PM2 logs for errors
echo ""
echo "📋 Recent PM2 logs:"
pm2 logs reddit-clone --lines 20 --nostream 2>&1 || true
'''
    
    print("\n🚀 Restarting Node.js app...")
    success, output = client.run_command(restart_app_script, timeout=180)
    print(output)
    
    # Final connectivity test
    import requests
    print("\n🌐 External Connectivity Test")
    print("-" * 30)
    
    endpoints = [
        ("Main App", f"http://{ip_address}/"),
        ("Health API", f"http://{ip_address}/api/health"),
    ]
    
    all_working = True
    for name, url in endpoints:
        try:
            print(f"Testing {name}...")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK (200)")
                if 'api' in url:
                    print(f"   Response: {response.text[:200]}")
            else:
                print(f"⚠️ {name}: HTTP {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"❌ {name}: Failed ({str(e)})")
            all_working = False
    
    print("\n" + "="*50)
    if all_working:
        print("🎉 Reddit Clone is now live!")
        print(f"🌐 Visit: http://{ip_address}/")
    else:
        print("⚠️ Some issues remain - check logs above")
    
    return 0 if all_working else 1

if __name__ == '__main__':
    sys.exit(main())
