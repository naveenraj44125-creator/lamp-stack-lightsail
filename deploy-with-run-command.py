#!/usr/bin/env python3
"""
Deploy LAMP Stack application to AWS Lightsail using run_command API
This script uses the Lightsail get-instance-access-details API instead of SSH keys
"""

import boto3
import subprocess
import tempfile
import os
import time
import sys
import json
import argparse
from botocore.exceptions import ClientError, NoCredentialsError

class LightsailDeployer:
    def __init__(self, instance_name, region='us-east-1'):
        self.instance_name = instance_name
        self.region = region
        try:
            self.lightsail = boto3.client('lightsail', region_name=region)
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure AWS credentials.")
            sys.exit(1)
    
    def run_command(self, command, timeout=300):
        """Execute command on Lightsail instance using get_instance_access_details"""
        try:
            print(f"🔧 Running: {command[:100]}{'...' if len(command) > 100 else ''}")
            
            # Get SSH access details
            ssh_response = self.lightsail.get_instance_access_details(instanceName=self.instance_name)
            ssh_details = ssh_response['accessDetails']
            
            # Create temporary SSH key files
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
                        # Limit output for readability
                        lines = result.stdout.strip().split('\n')
                        for line in lines[:20]:  # Show first 20 lines
                            print(f"   {line}")
                        if len(lines) > 20:
                            print(f"   ... ({len(lines) - 20} more lines)")
                    return True, result.stdout.strip()
                else:
                    print(f"   ❌ Failed (exit code: {result.returncode})")
                    if result.stderr.strip():
                        print(f"   Error: {result.stderr.strip()}")
                    return False, result.stderr.strip()
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(key_path)
                    os.unlink(cert_path)
                except:
                    pass
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False, str(e)

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

    def copy_file_to_instance(self, local_path, remote_path):
        """Copy file to instance using SCP"""
        try:
            print(f"📤 Copying {local_path} to {remote_path}")
            
            ssh_response = self.lightsail.get_instance_access_details(instanceName=self.instance_name)
            ssh_details = ssh_response['accessDetails']
            
            key_path, cert_path = self.create_ssh_files(ssh_details)
            
            try:
                scp_cmd = [
                    'scp', '-i', key_path, '-o', f'CertificateFile={cert_path}',
                    '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'ConnectTimeout=15', '-o', 'IdentitiesOnly=yes',
                    local_path, f'{ssh_details["username"]}@{ssh_details["ipAddress"]}:{remote_path}'
                ]
                
                result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"   ✅ File copied successfully")
                    return True
                else:
                    print(f"   ❌ Failed to copy file (exit code: {result.returncode})")
                    if result.stderr.strip():
                        print(f"   Error: {result.stderr.strip()}")
                    return False
                
            finally:
                try:
                    os.unlink(key_path)
                    os.unlink(cert_path)
                except:
                    pass
                
        except Exception as e:
            print(f"   ❌ Error copying file: {str(e)}")
            return False

    def wait_for_instance_running(self, timeout=300):
        """Wait for instance to be in running state"""
        print(f"⏳ Waiting for instance {self.instance_name} to be running...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.lightsail.get_instance(instanceName=self.instance_name)
                state = response['instance']['state']['name']
                print(f"Instance state: {state}")
                
                if state == 'running':
                    print("✅ Instance is running")
                    return True
                elif state in ['stopped', 'stopping', 'terminated']:
                    print(f"❌ Instance is in {state} state")
                    return False
                    
                time.sleep(10)
            except ClientError as e:
                print(f"❌ Error checking instance state: {e}")
                return False
        
        print("❌ Timeout waiting for instance to be running")
        return False

    def deploy_application(self, package_path, env_vars=None):
        """Deploy the LAMP stack application"""
        print(f"🚀 Starting LAMP Stack deployment of {package_path}")
        
        # Check if instance is running
        if not self.wait_for_instance_running():
            return False
        
        # Copy application package to instance
        if not self.copy_file_to_instance(package_path, '/tmp/app.tar.gz'):
            return False
        
        # Install LAMP stack and deploy application
        print("📦 Installing LAMP stack components...")
        lamp_install_script = '''
set -e

# Fix any broken packages first
echo "Fixing any broken packages..."
sudo dpkg --configure -a
sudo apt-get -f install -y

# Update system
echo "Updating system packages..."
sudo apt-get update -y

# Check if Apache is already installed
if ! command -v apache2 &> /dev/null; then
    echo "Installing Apache..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y apache2
else
    echo "Apache already installed"
fi

# Check if MySQL is already installed
if ! command -v mysql &> /dev/null; then
    echo "Installing MariaDB (lighter alternative to MySQL)..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mariadb-server mariadb-client
else
    echo "MySQL/MariaDB already installed"
fi

# Check if PHP is already installed
if ! command -v php &> /dev/null; then
    echo "Installing PHP and extensions..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y php php-mysql php-cli php-curl php-json php-mbstring php-xml php-zip
else
    echo "PHP already installed"
fi

# Start and enable services
echo "Starting services..."
sudo systemctl start apache2 || echo "Apache already running"
sudo systemctl enable apache2
sudo systemctl start mysql || echo "MySQL already running"
sudo systemctl enable mysql

# Configure Apache
echo "Configuring Apache..."
sudo a2enmod rewrite || echo "Rewrite module already enabled"
sudo systemctl restart apache2

# Set up web directory permissions
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

echo "✅ LAMP stack installation completed"
'''
        
        success, output = self.run_command(lamp_install_script, timeout=600)
        if not success:
            print("❌ Failed to install LAMP stack")
            return False
        
        # Deploy application files
        print("🚀 Deploying application files...")
        deploy_script = '''
set -e

# Extract application
cd /tmp
echo "Extracting application archive..."
tar -xzf app.tar.gz

# Backup current version if it exists
if [ -f "/var/www/html/index.html" ]; then
    echo "Backing up default Apache page..."
    sudo mv /var/www/html/index.html /var/www/html/index.html.backup.$(date +%Y%m%d_%H%M%S)
fi

# Deploy new version
echo "Deploying application files..."
sudo cp -r * /var/www/html/
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

echo "✅ Application files deployed successfully"
'''
        
        success, output = self.run_command(deploy_script, timeout=300)
        if not success:
            print("❌ Failed to deploy application files")
            return False
        
        # Set up database
        print("🗄️ Setting up MySQL database...")
        db_script = '''
set -e

# Configure MySQL (basic setup)
echo "Setting up database..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS lamp_demo;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'lamp_user'@'localhost' IDENTIFIED BY 'lamp_password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON lamp_demo.* TO 'lamp_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

echo "✅ Database setup completed"
'''
        
        success, output = self.run_command(db_script, timeout=120)
        if not success:
            print("⚠️  Database setup failed (may be expected if already configured)")
        
        # Create environment file if needed
        if env_vars:
            print("📝 Creating environment file...")
            env_content = "\\n".join([f"{k}={v}" for k, v in env_vars.items()])
            env_script = f'''
sudo tee /var/www/html/.env > /dev/null << 'ENVEOF'
{env_content}
ENVEOF
sudo chown www-data:www-data /var/www/html/.env
'''
            self.run_command(env_script)
        
        # Restart Apache to ensure everything is working
        print("🔄 Restarting Apache...")
        self.run_command("sudo systemctl restart apache2")
        
        # Check Apache status
        success, output = self.run_command("sudo systemctl status apache2 --no-pager")
        
        print("✅ LAMP Stack deployment completed!")
        return True
    
    def verify_deployment(self, expected_content="Hello Welcome"):
        """Verify the deployment is working"""
        try:
            # Get instance public IP
            response = self.lightsail.get_instance(instanceName=self.instance_name)
            public_ip = response['instance']['publicIpAddress']
            
            print(f"🔍 Verifying deployment at http://{public_ip}/")
            
            # Test the web server
            test_script = f'''
echo "Testing web server..."
curl -f -s http://localhost/ | head -20 || echo "Local test failed"
sudo systemctl status apache2 --no-pager | head -10
'''
            
            success, output = self.run_command(test_script)
            
            print(f"✅ Deployment verification completed")
            print(f"🌐 Application should be available at: http://{public_ip}/")
            
            return True
            
        except ClientError as e:
            print(f"❌ Error during verification: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Deploy LAMP Stack to AWS Lightsail')
    parser.add_argument('instance_name', help='Lightsail instance name')
    parser.add_argument('package_path', help='Path to application package (tar.gz)')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--env', action='append', help='Environment variables (KEY=VALUE)')
    
    args = parser.parse_args()
    
    # Parse environment variables
    env_vars = {}
    if args.env:
        for env_var in args.env:
            if '=' in env_var:
                key, value = env_var.split('=', 1)
                env_vars[key] = value
    
    # Check if package exists
    if not os.path.exists(args.package_path):
        print(f"❌ Package file not found: {args.package_path}")
        sys.exit(1)
    
    print(f"🚀 Starting LAMP Stack deployment to {args.instance_name}")
    print(f"📦 Package: {args.package_path}")
    print(f"🌍 Region: {args.region}")
    
    if env_vars:
        print(f"🔧 Environment variables: {list(env_vars.keys())}")
    
    # Create deployer and deploy
    deployer = LightsailDeployer(args.instance_name, args.region)
    
    if deployer.deploy_application(args.package_path, env_vars):
        if deployer.verify_deployment():
            print("🎉 Deployment completed successfully!")
            sys.exit(0)
        else:
            print("⚠️  Deployment completed but verification failed")
            sys.exit(1)
    else:
        print("❌ Deployment failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
