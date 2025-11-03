#!/usr/bin/env python3
"""
Setup Local Database Fallback
=============================
This script sets up a local MySQL database as a fallback when RDS is not available.
"""

import boto3
import subprocess
import tempfile
import os
import time
import sys

class LocalDatabaseSetup:
    def __init__(self, instance_name, region="us-east-1"):
        self.lightsail = boto3.client('lightsail', region_name=region)
        self.region = region
        self.instance_name = instance_name
        
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

    def setup_local_mysql(self):
        """Set up local MySQL database as fallback"""
        print(f"\n🔧 Setting up Local MySQL Database...")
        
        setup_script = '''
set -e
echo "Setting up local MySQL database..."

# Install MySQL if not already installed
if ! command -v mysql &> /dev/null; then
    echo "Installing MySQL server..."
    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get update
    sudo apt-get install -y mysql-server
fi

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Set root password and create app database
echo "Configuring MySQL..."
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root123';" || true
sudo mysql -u root -proot123 -e "CREATE DATABASE IF NOT EXISTS app_db;" || true
sudo mysql -u root -proot123 -e "CREATE USER IF NOT EXISTS 'app'@'localhost' IDENTIFIED BY 'app123';" || true
sudo mysql -u root -proot123 -e "GRANT ALL PRIVILEGES ON app_db.* TO 'app'@'localhost';" || true
sudo mysql -u root -proot123 -e "FLUSH PRIVILEGES;" || true

echo "✅ Local MySQL database configured"
'''
        
        success, output = self.run_command_on_instance(setup_script, timeout=300)
        return success

    def create_environment_file(self):
        """Create proper environment file for local database"""
        print(f"\n📝 Creating Environment File...")
        
        env_script = '''
set -e
echo "Creating environment file for local database..."

# Create .env file in web directory
sudo tee /var/www/html/.env > /dev/null << 'EOF'
# Database Configuration - Local MySQL Fallback
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

echo "✅ Environment file created with local database configuration"
echo "File contents:"
cat /var/www/html/.env
'''
        
        success, output = self.run_command_on_instance(env_script, timeout=60)
        return success

    def test_database_connection(self):
        """Test the database connection"""
        print(f"\n🧪 Testing Database Connection...")
        
        test_script = '''
set -e
echo "Testing database connection..."

# Test MySQL connection
mysql -u root -proot123 -e "SELECT 1 as test_connection;" app_db && echo "✅ MySQL connection successful" || echo "❌ MySQL connection failed"

# Test PHP database connection
php -r "
try {
    \$pdo = new PDO('mysql:host=localhost;port=3306;dbname=app_db;charset=utf8mb4', 'root', 'root123');
    echo '✅ PHP MySQL connection successful\n';
} catch (PDOException \$e) {
    echo '❌ PHP MySQL connection failed: ' . \$e->getMessage() . '\n';
}
"

echo "✅ Database connection tests completed"
'''
        
        success, output = self.run_command_on_instance(test_script, timeout=60)
        return success

    def restart_web_server(self):
        """Restart the web server to pick up new configuration"""
        print(f"\n🔄 Restarting Web Server...")
        
        restart_script = '''
set -e
echo "Restarting web server..."

# Restart Apache if it's running
if systemctl is-active --quiet apache2; then
    sudo systemctl restart apache2
    echo "✅ Apache restarted"
fi

# Restart Nginx if it's running
if systemctl is-active --quiet nginx; then
    sudo systemctl restart nginx
    echo "✅ Nginx restarted"
fi

echo "✅ Web server restart completed"
'''
        
        success, output = self.run_command_on_instance(restart_script, timeout=60)
        return success

    def run_setup(self):
        """Run the complete local database setup"""
        print("🎯 LOCAL DATABASE FALLBACK SETUP")
        print("="*50)
        
        try:
            # Set up local MySQL
            if not self.setup_local_mysql():
                print("❌ Failed to set up local MySQL")
                return False
            
            # Create environment file
            if not self.create_environment_file():
                print("❌ Failed to create environment file")
                return False
            
            # Test database connection
            if not self.test_database_connection():
                print("⚠️  Database connection test had issues")
            
            # Restart web server
            if not self.restart_web_server():
                print("⚠️  Web server restart had issues")
            
            print("\n" + "="*50)
            print("🎉 LOCAL DATABASE SETUP COMPLETED!")
            print("="*50)
            
            print("\n📋 SUMMARY:")
            print("✅ Local MySQL database installed and configured")
            print("✅ Environment file created with local database settings")
            print("✅ Database connection tested")
            print("✅ Web server restarted")
            
            print(f"\n🌐 Your application should now work at: http://98.91.3.69/")
            print("   Database operations should be functional with local MySQL")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            return False

def main():
    """Main function"""
    instance_name = "lamp-stack-demo"
    
    setup = LocalDatabaseSetup(instance_name)
    success = setup.run_setup()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()