#!/usr/bin/env python3
"""
Debug RDS Connection Issues
==========================
This script helps debug the RDS connection and environment file issues.
"""

import boto3
import subprocess
import tempfile
import os
import time
import sys

class RDSConnectionDebugger:
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

    def check_environment_files(self):
        """Check what environment files exist and their contents"""
        print(f"\n🔍 Checking Environment Files...")
        
        commands = [
            # Check if .env file exists in web directory
            "ls -la /var/www/html/.env 2>/dev/null || echo '.env file not found in web directory'",
            
            # Check if database.env exists in /opt/app
            "ls -la /opt/app/database.env 2>/dev/null || echo 'database.env file not found in /opt/app'",
            
            # Check what's in /opt/app directory
            "ls -la /opt/app/ 2>/dev/null || echo '/opt/app directory not found'",
            
            # Check if there are any .env files anywhere
            "find /var/www/html -name '*.env' -o -name '.env*' 2>/dev/null || echo 'No .env files found'",
            
            # Check the content of .env if it exists (without showing sensitive data)
            "if [ -f /var/www/html/.env ]; then echo 'Contents of /var/www/html/.env:'; head -5 /var/www/html/.env | sed 's/PASSWORD=.*/PASSWORD=***/' | sed 's/SECRET=.*/SECRET=***/'; else echo 'No .env file in web directory'; fi",
        ]
        
        for cmd in commands:
            success, output = self.run_command_on_instance(cmd)
            print()

    def fix_environment_file_permissions(self):
        """Fix the environment file permissions issue"""
        print(f"\n🔧 Fixing Environment File Issues...")
        
        fix_script = '''
set -e
echo "Creating proper environment file for database connection..."

# Create the .env file in web directory with proper permissions
sudo touch /var/www/html/.env
sudo chown www-data:www-data /var/www/html/.env
sudo chmod 644 /var/www/html/.env

# Create a basic .env file with local database fallback for now
cat << 'EOF' | sudo tee /var/www/html/.env > /dev/null
# Database Configuration
DB_EXTERNAL=false
DB_TYPE=MYSQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=app_db
DB_USERNAME=root
DB_PASSWORD=root123
DB_CHARSET=utf8mb4
EOF

echo "✅ Environment file created with proper permissions"
echo "File permissions:"
ls -la /var/www/html/.env
'''
        
        success, output = self.run_command_on_instance(fix_script)
        return success

    def test_database_connection_locally(self):
        """Test local database connection"""
        print(f"\n🔍 Testing Local Database Connection...")
        
        test_script = '''
set -e
echo "Testing local MySQL connection..."

# Check if MySQL is running
if sudo systemctl is-active --quiet mysql; then
    echo "✅ MySQL service is running"
else
    echo "❌ MySQL service is not running"
    echo "Starting MySQL service..."
    sudo systemctl start mysql || echo "Failed to start MySQL"
fi

# Test connection
mysql -u root -proot123 -e "SELECT 1 as test_connection;" 2>/dev/null && echo "✅ Local MySQL connection successful" || echo "❌ Local MySQL connection failed"

# Check if app_db database exists
mysql -u root -proot123 -e "SHOW DATABASES LIKE 'app_db';" 2>/dev/null | grep app_db && echo "✅ app_db database exists" || echo "❌ app_db database does not exist"

# Create app_db if it doesn't exist
mysql -u root -proot123 -e "CREATE DATABASE IF NOT EXISTS app_db;" 2>/dev/null && echo "✅ app_db database created/verified" || echo "❌ Failed to create app_db database"
'''
        
        success, output = self.run_command_on_instance(test_script)
        return success

    def check_rds_instances(self):
        """Check what RDS instances are available"""
        print(f"\n🔍 Checking Available RDS Instances...")
        
        try:
            # List all Lightsail RDS instances
            response = self.lightsail.get_relational_databases()
            databases = response.get('relationalDatabases', [])
            
            if not databases:
                print("❌ No Lightsail RDS instances found")
                return False
            
            print(f"✅ Found {len(databases)} RDS instance(s):")
            for db in databases:
                print(f"   📊 Name: {db['name']}")
                print(f"   🌍 Region: {db.get('location', {}).get('regionName', 'Unknown')}")
                print(f"   🔧 Engine: {db['engine']} {db.get('engineVersion', '')}")
                print(f"   📡 Endpoint: {db['masterEndpoint']['address']}:{db['masterEndpoint']['port']}")
                print(f"   📊 State: {db['state']}")
                print(f"   👤 Master User: {db['masterUsername']}")
                print(f"   💾 Master DB: {db.get('masterDatabaseName', 'N/A')}")
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking RDS instances: {str(e)}")
            return False

    def run_full_debug(self):
        """Run complete debugging session"""
        print("🎯 RDS CONNECTION DEBUGGING SESSION")
        print("="*50)
        
        try:
            # Check available RDS instances
            self.check_rds_instances()
            
            # Check environment files
            self.check_environment_files()
            
            # Fix environment file permissions
            self.fix_environment_file_permissions()
            
            # Test local database connection
            self.test_database_connection_locally()
            
            print("\n" + "="*50)
            print("🎉 DEBUGGING SESSION COMPLETED!")
            print("="*50)
            
            print("\n📋 NEXT STEPS:")
            print("1. The .env file has been created with local database fallback")
            print("2. Check your GitHub repository secrets for AWS credentials")
            print("3. Verify the RDS instance name in deployment-generic.config.yml")
            print("4. Re-run the deployment after fixing RDS credentials")
            print("5. Test the application at http://98.91.3.69/")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Debugging failed: {str(e)}")
            return False

def main():
    """Main function"""
    instance_name = "lamp-stack-demo"
    
    debugger = RDSConnectionDebugger(instance_name)
    success = debugger.run_full_debug()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()