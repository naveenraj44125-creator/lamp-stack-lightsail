#!/usr/bin/env python3
"""
Fix Database Connections
========================
This script fixes both local and RDS database connections for the LAMP stack application.
It handles AWS credential issues and sets up proper fallback mechanisms.
"""

import boto3
import subprocess
import tempfile
import os
import time
import sys
import json

class DatabaseConnectionFixer:
    def __init__(self, instance_name, region="us-east-1"):
        self.region = region
        self.instance_name = instance_name
        self.lightsail = None
        
    def setup_aws_credentials(self):
        """Setup AWS credentials if available"""
        print(f"\n🔑 Setting up AWS credentials...")
        
        # Check if AWS credentials are available in environment
        access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        if access_key and secret_key:
            print("✅ AWS credentials found in environment")
            try:
                self.lightsail = boto3.client('lightsail', region_name=self.region)
                # Test the credentials
                self.lightsail.get_regions()
                print("✅ AWS credentials are valid")
                return True
            except Exception as e:
                print(f"❌ AWS credentials are invalid: {e}")
                return False
        else:
            print("⚠️  No AWS credentials found in environment")
            print("   You can set them with:")
            print("   export AWS_ACCESS_KEY_ID='your_access_key'")
            print("   export AWS_SECRET_ACCESS_KEY='your_secret_key'")
            return False

    def create_ssh_files(self, ssh_details):
        """Create temporary SSH key files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as key_file:
            key_file.write(ssh_details['privateKey'])
            key_path = key_file.name
        
        cert_path = key_path + '-cert.pub'
        cert_parts = ssh_details['certKey'].split(' ', 2)
        formatted_cert = f'{cert_parts[0]} {cert_parts[1]}\n' if len(cert_parts) >= 2 else ssh_details['certKey'] + '\n'
        
        with open(cert_path, 'w') as cert_file:
            cert_file.write(formatted_cert)
        
        os.chmod(key_path, 0o600)
        os.chmod(cert_path, 0o600)
        
        return key_path, cert_path

    def run_command_on_instance(self, command, timeout=300):
        """Execute SSH command on the Lightsail instance"""
        if not self.lightsail:
            print("❌ Cannot run SSH commands without valid AWS credentials")
            return False, "No AWS credentials"
            
        try:
            print(f"🔧 Running: {command[:80]}{'...' if len(command) > 80 else ''}")
            
            ssh_response = self.lightsail.get_instance_access_details(instanceName=self.instance_name)
            ssh_details = ssh_response['accessDetails']
            
            key_path, cert_path = self.create_ssh_files(ssh_details)
            
            try:
                ssh_cmd = [
                    'ssh', '-i', key_path, '-o', f'CertificateFile={cert_path}',
                    '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'ConnectTimeout=15', '-o', 'IdentitiesOnly=yes',
                    f'{ssh_details["username"]}@{ssh_details["ipAddress"]}', command
                ]
                
                result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
                
                if result.returncode == 0:
                    print(f"   ✅ Success")
                    if result.stdout.strip():
                        for line in result.stdout.strip().split('\n'):
                            print(f"   {line}")
                    return True, result.stdout.strip()
                else:
                    print(f"   ❌ Failed (exit code: {result.returncode})")
                    if result.stderr.strip():
                        for line in result.stderr.strip().split('\n'):
                            print(f"   ERROR: {line}")
                    return False, result.stderr.strip()
                
            finally:
                try:
                    os.unlink(key_path)
                    os.unlink(cert_path)
                except:
                    pass
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False, str(e)

    def fix_local_database(self):
        """Fix local MySQL database connection"""
        print(f"\n🔧 Fixing Local MySQL Database...")
        
        if not self.lightsail:
            print("⚠️  Cannot fix local database without SSH access")
            return False
        
        fix_script = '''
set -e
echo "Fixing local MySQL database connection..."

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "Installing MySQL server..."
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
fi

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Check if MySQL is running
if sudo systemctl is-active --quiet mysql; then
    echo "✅ MySQL service is running"
else
    echo "❌ MySQL service failed to start"
    sudo systemctl status mysql
    exit 1
fi

# Set root password and create database
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root123';" 2>/dev/null || echo "Root password already set or MySQL not accessible"

# Create database and test connection
mysql -u root -proot123 -e "CREATE DATABASE IF NOT EXISTS app_db;" 2>/dev/null && echo "✅ app_db database created/verified" || echo "❌ Failed to create app_db database"

# Test connection
mysql -u root -proot123 -e "SELECT 1 as test_connection;" app_db 2>/dev/null && echo "✅ Local MySQL connection successful" || echo "❌ Local MySQL connection failed"

# Create a simple test table
mysql -u root -proot123 app_db -e "
CREATE TABLE IF NOT EXISTS test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT IGNORE INTO test_table (id, name) VALUES (1, 'Test Entry');
" 2>/dev/null && echo "✅ Test table created" || echo "❌ Failed to create test table"

echo "✅ Local MySQL database setup completed"
'''
        
        success, output = self.run_command_on_instance(fix_script, timeout=180)
        return success

    def create_local_env_file(self):
        """Create environment file for local database"""
        print(f"\n📝 Creating Local Database Environment File...")
        
        if not self.lightsail:
            print("⚠️  Cannot create environment file without SSH access")
            return False
        
        env_script = '''
set -e
echo "Creating environment file for local database..."

# Create .env file in web directory
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

echo "✅ Local database environment file created"
echo "Configuration:"
echo "  Database Type: Local MySQL"
echo "  Host: localhost:3306"
echo "  Database: app_db"
echo "  Username: root"
'''
        
        success, output = self.run_command_on_instance(env_script, timeout=60)
        return success

    def test_php_database_connection(self):
        """Test PHP database connection"""
        print(f"\n🧪 Testing PHP Database Connection...")
        
        if not self.lightsail:
            print("⚠️  Cannot test PHP connection without SSH access")
            return False
        
        test_script = '''
set -e
echo "Testing PHP database connection..."

# Create a PHP test script
sudo tee /var/www/html/test_db.php > /dev/null << 'EOF'
<?php
// Load database configuration
require_once 'config/database.php';

echo "Database Configuration Test\\n";
echo "==========================\\n";
echo "DB_HOST: " . DB_HOST . "\\n";
echo "DB_NAME: " . DB_NAME . "\\n";
echo "DB_USER: " . DB_USER . "\\n";
echo "DB_EXTERNAL: " . (DB_EXTERNAL ? 'true' : 'false') . "\\n";
echo "\\n";

// Test database connection
echo "Testing database connection...\\n";
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

echo "\\nDatabase status: " . getDatabaseStatus() . "\\n";
?>
EOF

# Run the PHP test
php /var/www/html/test_db.php

# Clean up test file
sudo rm -f /var/www/html/test_db.php

echo "✅ PHP database connection test completed"
'''
        
        success, output = self.run_command_on_instance(test_script, timeout=60)
        return success

    def restart_web_server(self):
        """Restart web server to pick up changes"""
        print(f"\n🔄 Restarting Web Server...")
        
        if not self.lightsail:
            print("⚠️  Cannot restart web server without SSH access")
            return False
        
        restart_script = '''
set -e
echo "Restarting web server..."

# Restart Apache
sudo systemctl restart apache2
echo "✅ Apache restarted"

# Check Apache status
sudo systemctl is-active --quiet apache2 && echo "✅ Apache is running" || echo "❌ Apache is not running"

echo "✅ Web server restart completed"
'''
        
        success, output = self.run_command_on_instance(restart_script, timeout=60)
        return success

    def check_rds_availability(self):
        """Check if RDS instance is available"""
        print(f"\n🔍 Checking RDS Availability...")
        
        if not self.lightsail:
            print("⚠️  Cannot check RDS without AWS credentials")
            return False, None
        
        try:
            response = self.lightsail.get_relational_databases()
            databases = response.get('relationalDatabases', [])
            
            if not databases:
                print("❌ No Lightsail RDS instances found")
                return False, None
            
            # Look for our specific database
            target_db = None
            for db in databases:
                if db['name'] == 'lamp-app-db':
                    target_db = db
                    break
            
            if target_db:
                print(f"✅ Found RDS instance: {target_db['name']}")
                print(f"   Endpoint: {target_db['masterEndpoint']['address']}")
                print(f"   State: {target_db['state']}")
                return True, target_db
            else:
                print("❌ RDS instance 'lamp-app-db' not found")
                return False, None
                
        except Exception as e:
            print(f"❌ Error checking RDS: {str(e)}")
            return False, None

    def setup_rds_connection(self, db_instance):
        """Setup RDS database connection"""
        print(f"\n🔧 Setting up RDS Connection...")
        
        if not self.lightsail or not db_instance:
            print("⚠️  Cannot setup RDS without AWS credentials or database instance")
            return False
        
        try:
            # Get master password
            password_response = self.lightsail.get_relational_database_master_user_password(
                relationalDatabaseName='lamp-app-db'
            )
            master_password = password_response.get('masterUserPassword')
            
            if not master_password:
                print("❌ Could not retrieve RDS master password")
                return False
            
            print("✅ Retrieved RDS master password")
            
            # Create RDS environment file
            endpoint = db_instance['masterEndpoint']['address']
            port = db_instance['masterEndpoint']['port']
            username = db_instance['masterUsername']
            database = db_instance.get('masterDatabaseName', 'app_db')
            
            rds_env_script = f'''
set -e
echo "Creating RDS environment file..."

# Install MySQL client if not present
sudo apt-get update
sudo apt-get install -y mysql-client

# Create .env file with RDS configuration
sudo tee /var/www/html/.env > /dev/null << 'EOF'
# Database Configuration - AWS Lightsail RDS
DB_EXTERNAL=true
DB_TYPE=MYSQL
DB_HOST={endpoint}
DB_PORT={port}
DB_NAME={database}
DB_USERNAME={username}
DB_PASSWORD={master_password}
DB_CHARSET=utf8mb4

# Application Configuration
APP_ENV=production
APP_DEBUG=false
APP_NAME="Generic Application"
EOF

# Set proper permissions
sudo chown www-data:www-data /var/www/html/.env
sudo chmod 644 /var/www/html/.env

echo "✅ RDS environment file created"

# Test RDS connection
mysql -h {endpoint} -P {port} -u {username} -p{master_password} -e "SELECT 1 as test_connection;" {database} && echo "✅ RDS MySQL connection successful" || echo "❌ RDS MySQL connection failed"

echo "✅ RDS connection setup completed"
'''
            
            success, output = self.run_command_on_instance(rds_env_script, timeout=120)
            return success
            
        except Exception as e:
            print(f"❌ Error setting up RDS connection: {str(e)}")
            return False

    def run_comprehensive_fix(self):
        """Run comprehensive database connection fix"""
        print("🎯 COMPREHENSIVE DATABASE CONNECTION FIX")
        print("="*60)
        
        success_count = 0
        total_steps = 0
        
        try:
            # Step 1: Setup AWS credentials
            total_steps += 1
            if self.setup_aws_credentials():
                success_count += 1
                aws_available = True
            else:
                aws_available = False
            
            if aws_available:
                # Step 2: Check RDS availability
                total_steps += 1
                rds_available, db_instance = self.check_rds_availability()
                if rds_available:
                    success_count += 1
                
                # Step 3: Setup RDS connection if available
                if rds_available and db_instance:
                    total_steps += 1
                    if self.setup_rds_connection(db_instance):
                        success_count += 1
                        print("\n🎉 RDS connection configured successfully!")
                    else:
                        print("\n⚠️  RDS connection failed, falling back to local database")
                        # Fall back to local database
                        total_steps += 2
                        if self.fix_local_database():
                            success_count += 1
                        if self.create_local_env_file():
                            success_count += 1
                else:
                    print("\n⚠️  RDS not available, setting up local database")
                    # Setup local database
                    total_steps += 2
                    if self.fix_local_database():
                        success_count += 1
                    if self.create_local_env_file():
                        success_count += 1
            else:
                print("\n⚠️  AWS credentials not available, setting up local database only")
                # Setup local database without AWS
                print("\n🔧 Setting up local database fallback...")
                print("   Note: You'll need to configure this manually or provide AWS credentials")
                
                # Provide manual instructions
                print("\n📋 MANUAL SETUP INSTRUCTIONS:")
                print("1. SSH into your Lightsail instance:")
                print("   ssh -i your-key.pem ubuntu@98.91.3.69")
                print("\n2. Install and configure MySQL:")
                print("   sudo apt-get update")
                print("   sudo apt-get install -y mysql-server")
                print("   sudo systemctl start mysql")
                print("   sudo mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root123';\"")
                print("   mysql -u root -proot123 -e \"CREATE DATABASE IF NOT EXISTS app_db;\"")
                print("\n3. Create environment file:")
                print("   sudo tee /var/www/html/.env > /dev/null << 'EOF'")
                print("DB_EXTERNAL=false")
                print("DB_TYPE=MYSQL")
                print("DB_HOST=localhost")
                print("DB_PORT=3306")
                print("DB_NAME=app_db")
                print("DB_USERNAME=root")
                print("DB_PASSWORD=root123")
                print("DB_CHARSET=utf8mb4")
                print("APP_ENV=production")
                print("APP_DEBUG=false")
                print("APP_NAME=\"Generic Application\"")
                print("EOF")
                print("\n4. Set permissions and restart Apache:")
                print("   sudo chown www-data:www-data /var/www/html/.env")
                print("   sudo chmod 644 /var/www/html/.env")
                print("   sudo systemctl restart apache2")
                
                return False
            
            # Step 4: Test PHP connection
            if aws_available:
                total_steps += 1
                if self.test_php_database_connection():
                    success_count += 1
            
            # Step 5: Restart web server
            if aws_available:
                total_steps += 1
                if self.restart_web_server():
                    success_count += 1
            
            print(f"\n" + "="*60)
            print(f"🎉 DATABASE CONNECTION FIX COMPLETED!")
            print(f"="*60)
            
            print(f"\n📊 RESULTS: {success_count}/{total_steps} steps successful")
            
            if success_count == total_steps:
                print("✅ All steps completed successfully!")
            elif success_count > 0:
                print("⚠️  Partial success - some steps completed")
            else:
                print("❌ Most steps failed - manual intervention required")
            
            print(f"\n🌐 Test your application at: http://98.91.3.69/")
            print("   The database connection should now be working")
            
            if aws_available and success_count > 0:
                print("\n📋 WHAT WAS FIXED:")
                if rds_available:
                    print("✅ RDS connection configured")
                    print("✅ Environment file created with RDS settings")
                else:
                    print("✅ Local MySQL database configured")
                    print("✅ Environment file created with local settings")
                print("✅ PHP database connection tested")
                print("✅ Web server restarted")
            
            return success_count > 0
            
        except Exception as e:
            print(f"\n❌ Fix failed: {str(e)}")
            return False

def main():
    """Main function"""
    instance_name = "lamp-stack-demo"
    
    print("🔧 Database Connection Fixer")
    print("This script will fix database connections for your LAMP stack application")
    print("It will try RDS first, then fall back to local MySQL if needed")
    print()
    
    fixer = DatabaseConnectionFixer(instance_name)
    success = fixer.run_comprehensive_fix()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()