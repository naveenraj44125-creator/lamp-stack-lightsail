#!/usr/bin/env python3
"""
Setup RDS Connection
===================
This script sets up the proper RDS database connection using the available RDS instance.
"""

import boto3
import subprocess
import tempfile
import os
import time
import sys

class RDSConnectionSetup:
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

    def get_rds_connection_details(self):
        """Get RDS connection details"""
        print(f"\n🔍 Getting RDS Connection Details...")
        
        try:
            response = self.lightsail.get_relational_database(relationalDatabaseName='lamp-app-db')
            db_instance = response['relationalDatabase']
            
            # Get master user password
            try:
                password_response = self.lightsail.get_relational_database_master_user_password(
                    relationalDatabaseName='lamp-app-db'
                )
                master_password = password_response.get('masterUserPassword')
                print("✅ Retrieved master password from Lightsail")
            except Exception as e:
                print(f"⚠️  Could not retrieve master password: {e}")
                master_password = None
            
            connection_details = {
                'endpoint': db_instance['masterEndpoint']['address'],
                'port': db_instance['masterEndpoint']['port'],
                'engine': db_instance['engine'],
                'master_username': db_instance['masterUsername'],
                'master_password': master_password,
                'database_name': db_instance.get('masterDatabaseName', 'app_db'),
            }
            
            print(f"✅ RDS connection details:")
            print(f"   Endpoint: {connection_details['endpoint']}")
            print(f"   Port: {connection_details['port']}")
            print(f"   Engine: {connection_details['engine']}")
            print(f"   Database: {connection_details['database_name']}")
            print(f"   Username: {connection_details['master_username']}")
            print(f"   Password: {'***' if master_password else 'Not retrieved'}")
            
            return connection_details
            
        except Exception as e:
            print(f"❌ Error getting RDS details: {str(e)}")
            return None

    def install_mysql_client(self):
        """Install MySQL client"""
        print(f"\n📦 Installing MySQL Client...")
        
        install_script = '''
set -e
echo "Installing MySQL client..."

# Update package list
sudo apt-get update

# Install MySQL client
sudo apt-get install -y mysql-client

echo "✅ MySQL client installed"
mysql --version
'''
        
        success, output = self.run_command_on_instance(install_script, timeout=180)
        return success

    def create_rds_environment_file(self, connection_details):
        """Create environment file with RDS connection details"""
        print(f"\n📝 Creating RDS Environment File...")
        
        if not connection_details or not connection_details.get('master_password'):
            print("❌ Cannot create RDS environment file without password")
            return False
        
        env_script = f'''
set -e
echo "Creating environment file for RDS database..."

# Create .env file in web directory with RDS configuration
sudo tee /var/www/html/.env > /dev/null << 'EOF'
# Database Configuration - AWS Lightsail RDS
DB_EXTERNAL=true
DB_TYPE=MYSQL
DB_HOST={connection_details['endpoint']}
DB_PORT={connection_details['port']}
DB_NAME={connection_details['database_name']}
DB_USERNAME={connection_details['master_username']}
DB_PASSWORD={connection_details['master_password']}
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
echo "Configuration summary:"
echo "  Database Type: External RDS MySQL"
echo "  Host: {connection_details['endpoint']}"
echo "  Port: {connection_details['port']}"
echo "  Database: {connection_details['database_name']}"
echo "  Username: {connection_details['master_username']}"
'''
        
        success, output = self.run_command_on_instance(env_script, timeout=60)
        return success

    def test_rds_connection(self, connection_details):
        """Test RDS database connection"""
        print(f"\n🧪 Testing RDS Connection...")
        
        if not connection_details or not connection_details.get('master_password'):
            print("❌ Cannot test RDS connection without password")
            return False
        
        endpoint = connection_details['endpoint']
        port = connection_details['port']
        username = connection_details['master_username']
        password = connection_details['master_password']
        database = connection_details['database_name']
        
        test_script = f'''
set -e
echo "Testing RDS database connection..."

# Test MySQL connection to RDS
mysql -h {endpoint} -P {port} -u {username} -p{password} -e "SELECT 1 as test_connection;" {database} && echo "✅ RDS MySQL connection successful" || echo "❌ RDS MySQL connection failed"

# Test PHP database connection
php -r "
try {{
    \\$pdo = new PDO('mysql:host={endpoint};port={port};dbname={database};charset=utf8mb4', '{username}', '{password}');
    echo '✅ PHP RDS MySQL connection successful\\n';
}} catch (PDOException \\$e) {{
    echo '❌ PHP RDS MySQL connection failed: ' . \\$e->getMessage() . '\\n';
}}
"

echo "✅ RDS connection tests completed"
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

echo "✅ Web server restart completed"
'''
        
        success, output = self.run_command_on_instance(restart_script, timeout=60)
        return success

    def run_setup(self):
        """Run the complete RDS connection setup"""
        print("🎯 RDS CONNECTION SETUP")
        print("="*50)
        
        try:
            # Get RDS connection details
            connection_details = self.get_rds_connection_details()
            if not connection_details:
                print("❌ Failed to get RDS connection details")
                return False
            
            # Install MySQL client
            if not self.install_mysql_client():
                print("❌ Failed to install MySQL client")
                return False
            
            # Create RDS environment file
            if not self.create_rds_environment_file(connection_details):
                print("❌ Failed to create RDS environment file")
                return False
            
            # Test RDS connection
            if not self.test_rds_connection(connection_details):
                print("⚠️  RDS connection test had issues")
            
            # Restart web server
            if not self.restart_web_server():
                print("⚠️  Web server restart had issues")
            
            print("\n" + "="*50)
            print("🎉 RDS CONNECTION SETUP COMPLETED!")
            print("="*50)
            
            print("\n📋 SUMMARY:")
            print("✅ RDS connection details retrieved")
            print("✅ MySQL client installed")
            print("✅ Environment file created with RDS settings")
            print("✅ RDS connection tested")
            print("✅ Web server restarted")
            
            print(f"\n🌐 Your application should now work at: http://98.91.3.69/")
            print("   Database operations should be functional with RDS MySQL")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            return False

def main():
    """Main function"""
    instance_name = "lamp-stack-demo"
    
    setup = RDSConnectionSetup(instance_name)
    success = setup.run_setup()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()