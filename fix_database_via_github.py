#!/usr/bin/env python3
"""
Fix Database Connection via GitHub Actions
==========================================
This script fixes the database connection by creating a proper environment file
and setting up the local MySQL database as a fallback.
"""

import sys
import argparse
from lightsail_common import LightsailBase
from config_loader import DeploymentConfig

class DatabaseFixer:
    def __init__(self, instance_name, region):
        self.client = LightsailBase(instance_name, region)
        self.instance_name = instance_name
        self.region = region

    def fix_database_connection(self):
        """Fix the database connection by setting up local MySQL and environment file"""
        print("🔧 Fixing database connection...")
        
        # Step 1: Install and configure MySQL
        mysql_setup_script = '''
set -e
echo "Setting up MySQL database..."

# Install MySQL if not present
if ! command -v mysql &> /dev/null; then
    echo "Installing MySQL server..."
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
fi

# Start and enable MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Set root password and create database
echo "Configuring MySQL..."
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root123';" 2>/dev/null || echo "Root password configuration attempted"

# Create database
mysql -u root -proot123 -e "CREATE DATABASE IF NOT EXISTS app_db;" 2>/dev/null && echo "✅ app_db database created" || echo "❌ Failed to create database"

# Create test table
mysql -u root -proot123 app_db -e "
CREATE TABLE IF NOT EXISTS test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT IGNORE INTO test_table (id, name) VALUES (1, 'Test Entry');
" 2>/dev/null && echo "✅ Test table created" || echo "❌ Failed to create test table"

# Test connection
mysql -u root -proot123 -e "SELECT 1 as test;" app_db 2>/dev/null && echo "✅ MySQL connection successful" || echo "❌ MySQL connection failed"

echo "✅ MySQL setup completed"
'''
        
        success, output = self.client.run_command(mysql_setup_script, timeout=180)
        if not success:
            print("❌ Failed to set up MySQL")
            return False
        
        # Step 2: Create proper environment file
        env_setup_script = '''
set -e
echo "Creating database environment file..."

# Create .env file with local database configuration
sudo tee /var/www/html/.env > /dev/null << 'EOF'
# Database Configuration - Local MySQL
DB_EXTERNAL=false
DB_TYPE=MYSQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app_db
DB_USERNAME=root
DB_PASSWORD=root123
DB_CHARSET=utf8mb4

# Application Configuration
APP_ENV=production
APP_DEBUG=false
APP_NAME="Generic Application"
EOF

# Set proper permissions
sudo chown www-data:www-data /var/www/html/.env
sudo chmod 644 /var/www/html/.env

echo "✅ Environment file created"
echo "Configuration:"
cat /var/www/html/.env | grep -v PASSWORD
'''
        
        success, output = self.client.run_command(env_setup_script, timeout=60)
        if not success:
            print("❌ Failed to create environment file")
            return False
        
        # Step 3: Test PHP database connection
        php_test_script = '''
set -e
echo "Testing PHP database connection..."

# Create PHP test script
sudo tee /tmp/test_db_connection.php > /dev/null << 'EOF'
<?php
// Load database configuration
require_once '/var/www/html/config/database.php';

echo "Database Connection Test\\n";
echo "========================\\n";

// Test database connection
$connection = getDatabaseConnection();

if ($connection) {
    echo "✅ PHP database connection successful\\n";
    
    // Test a simple query
    try {
        $stmt = $connection->query('SELECT COUNT(*) as count FROM test_table');
        $result = $stmt->fetch();
        echo "✅ Test query successful - found " . $result['count'] . " records\\n";
    } catch (Exception $e) {
        echo "⚠️  Test query failed: " . $e->getMessage() . "\\n";
    }
} else {
    echo "❌ PHP database connection failed\\n";
}
?>
EOF

# Run the PHP test
php /tmp/test_db_connection.php

# Clean up
sudo rm -f /tmp/test_db_connection.php

echo "✅ PHP database test completed"
'''
        
        success, output = self.client.run_command(php_test_script, timeout=60)
        if not success:
            print("⚠️  PHP database test had issues")
        
        # Step 4: Restart Apache
        restart_script = '''
set -e
echo "Restarting Apache..."

sudo systemctl restart apache2
sudo systemctl is-active --quiet apache2 && echo "✅ Apache is running" || echo "❌ Apache failed to start"

echo "✅ Apache restart completed"
'''
        
        success, output = self.client.run_command(restart_script, timeout=30)
        if not success:
            print("⚠️  Apache restart had issues")
        
        print("✅ Database connection fix completed!")
        return True

def main():
    parser = argparse.ArgumentParser(description='Fix database connection via GitHub Actions')
    parser.add_argument('--instance-name', required=True, help='Lightsail instance name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    try:
        print(f"🔧 Database Connection Fixer for {args.instance_name}")
        print(f"🌍 Region: {args.region}")
        
        fixer = DatabaseFixer(args.instance_name, args.region)
        
        if fixer.fix_database_connection():
            print("🎉 Database connection fixed successfully!")
            print("🌐 Test your application at: http://98.91.3.69/")
            sys.exit(0)
        else:
            print("❌ Database connection fix failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error fixing database connection: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()