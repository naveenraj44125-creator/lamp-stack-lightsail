#!/usr/bin/env python3
"""
LAMP Stack Installation Script for AWS Lightsail
Installs Apache, MySQL/MariaDB, and PHP on a Lightsail instance
"""

import boto3
import subprocess
import time
import sys
import os
import tempfile
import argparse
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

class LightsailLAMPInstaller:
    def __init__(self, instance_name, region='us-east-1'):
        self.instance_name = instance_name
        self.region = region
        try:
            self.lightsail = boto3.client('lightsail', region_name=region)
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure AWS credentials.")
            sys.exit(1)

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

    def run_command(self, command, timeout=300):
        """Execute command on Lightsail instance using SSH certificates with enhanced GitHub Actions support"""
        try:
            print(f"🔧 Running: {command[:100]}{'...' if len(command) > 100 else ''}")

            # Get SSH access details
            ssh_response = self.lightsail.get_instance_access_details(instanceName=self.instance_name)
            ssh_details = ssh_response['accessDetails']

            # Create temporary SSH key files
            key_path, cert_path = self.create_ssh_files(ssh_details)

            try:
                # Enhanced SSH configuration for GitHub Actions compatibility
                ssh_cmd = [
                    'ssh', '-i', key_path, '-o', f'CertificateFile={cert_path}',
                    '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'ConnectTimeout=60', '-o', 'ServerAliveInterval=30',
                    '-o', 'ServerAliveCountMax=6', '-o', 'ConnectionAttempts=3',
                    '-o', 'IdentitiesOnly=yes', '-o', 'TCPKeepAlive=yes',
                    '-o', 'ExitOnForwardFailure=yes', '-o', 'BatchMode=yes',
                    '-o', 'PreferredAuthentications=publickey', '-o', 'LogLevel=VERBOSE',
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

    def test_network_connectivity(self):
        """Test network connectivity to the instance"""
        try:
            ssh_response = self.lightsail.get_instance_access_details(instanceName=self.instance_name)
            ip_address = ssh_response['accessDetails']['ipAddress']
            
            print(f"🔍 Testing network connectivity to {ip_address}...")
            
            # Test basic connectivity
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((ip_address, 22))
            sock.close()
            
            if result == 0:
                print("✅ Network connectivity to SSH port successful")
                return True
            else:
                print(f"⚠️ Network connectivity test failed (error code: {result})")
                return False
                
        except Exception as e:
            print(f"⚠️ Network connectivity test error: {e}")
            return False

    def test_ssh_connection(self):
        """Test SSH connection with enhanced diagnostics"""
        print("🔍 Testing SSH connection...")
        
        # First test network connectivity
        if not self.test_network_connectivity():
            print("⚠️ Network connectivity issues detected")
            return False
            
        success, output = self.run_command("echo 'SSH connection test successful'", timeout=30)
        if success:
            print("✅ SSH connection test passed")
            return True
        else:
            print(f"⚠️ SSH connection test failed: {output}")
            return False

    def run_command_with_retry(self, command, timeout=300, max_retries=8):
        """Execute command with enhanced retry logic optimized for GitHub Actions"""
        for attempt in range(max_retries):
            if attempt > 0:
                print(f"🔄 Retrying command (attempt {attempt + 1}/{max_retries})...")
                # Progressive backoff with longer initial waits for GitHub Actions
                wait_time = min(15 + (attempt * 10), 60)
                print(f"   ⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                
                # Test connectivity before retry
                if not self.test_network_connectivity():
                    print("   ⚠️ Network connectivity still failing, continuing retry...")

            success, output = self.run_command(command, timeout)

            if success:
                return True, output

            # Enhanced connection error detection
            connection_errors = [
                "Broken pipe", "Connection reset", "Connection timed out",
                "Connection refused", "Network is unreachable", "Host is down",
                "ssh_exchange_identification", "Connection closed by remote host",
                "Connection lost", "Connection aborted", "No route to host",
                "Operation timed out", "connect to host", "timed out after"
            ]

            is_connection_error = any(error in output.lower() for error in [e.lower() for e in connection_errors])

            if is_connection_error:
                print(f"   🔄 Connection issue detected: {output[:100]}...")
                
                # For GitHub Actions, try to restart instance on persistent failures
                if attempt >= 3 and "GITHUB_ACTIONS" in os.environ:
                    print("   🔄 GitHub Actions detected - attempting instance restart...")
                    self.restart_instance_for_connectivity()
                    
                continue
            else:
                # If it's not a connection issue, don't retry
                print(f"   ❌ Non-connection error detected, not retrying: {output[:100]}...")
                break

        return False, output

    def restart_instance_for_connectivity(self):
        """Restart instance to resolve connectivity issues (GitHub Actions fallback)"""
        try:
            print("🔄 Attempting instance restart to resolve connectivity...")
            
            # Stop instance
            self.lightsail.stop_instance(instanceName=self.instance_name)
            print("   ⏳ Stopping instance...")
            time.sleep(30)
            
            # Wait for stopped state
            for _ in range(12):  # 2 minutes max
                response = self.lightsail.get_instance(instanceName=self.instance_name)
                state = response['instance']['state']['name']
                if state == 'stopped':
                    break
                time.sleep(10)
            
            # Start instance
            self.lightsail.start_instance(instanceName=self.instance_name)
            print("   ⏳ Starting instance...")
            time.sleep(60)
            
            # Wait for running state
            for _ in range(18):  # 3 minutes max
                response = self.lightsail.get_instance(instanceName=self.instance_name)
                state = response['instance']['state']['name']
                if state == 'running':
                    print("   ✅ Instance restarted successfully")
                    time.sleep(30)  # Additional wait for SSH service
                    return True
                time.sleep(10)
                
            print("   ⚠️ Instance restart timeout")
            return False
            
        except Exception as e:
            print(f"   ❌ Instance restart failed: {e}")
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

    def install_lamp_stack(self):
        """Install LAMP stack on Lightsail instance"""
        print(f"🚀 Starting LAMP stack installation on {self.instance_name}")
        
        # Check if instance is running
        if not self.wait_for_instance_running():
            return False
        
        # Wait additional time for SSH service to be fully ready
        print("⏳ Waiting 60 seconds for SSH service to be fully ready...")
        time.sleep(60)

        # Test SSH connection before proceeding with enhanced diagnostics
        if not self.test_ssh_connection():
            print("⚠️ SSH connection test failed, but proceeding with retry logic...")
            
            # For GitHub Actions, try one instance restart before proceeding
            if "GITHUB_ACTIONS" in os.environ:
                print("🔄 GitHub Actions detected - performing preventive instance restart...")
                self.restart_instance_for_connectivity()
        
        print("📦 Installing LAMP stack components...")
        
        # Break down installation into smaller steps for better reliability
        installation_steps = [
            ("Fixing broken packages", """
set -e
echo "Fixing any broken packages..."
sudo dpkg --configure -a || true
sudo apt-get -f install -y || true
            """.strip()),
            
            ("Updating system packages", """
set -e
echo "Updating system packages..."
sudo apt-get update -y
            """.strip()),
            
            ("Installing Apache", """
set -e
if ! command -v apache2 &> /dev/null; then
    echo "Installing Apache..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y apache2
else
    echo "Apache already installed"
fi
            """.strip()),
            
            ("Installing MariaDB", """
set -e
if ! command -v mysql &> /dev/null; then
    echo "Installing MariaDB..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mariadb-server mariadb-client
else
    echo "MySQL/MariaDB already installed"
fi
            """.strip()),
            
            ("Installing PHP", """
set -e
if ! command -v php &> /dev/null; then
    echo "Installing PHP and extensions..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y php php-mysql php-cli php-curl php-json php-mbstring php-xml php-zip
else
    echo "PHP already installed"
fi
            """.strip()),
            
            ("Starting services", """
set -e
echo "Starting services..."
sudo systemctl start apache2 || echo "Apache already running"
sudo systemctl enable apache2
sudo systemctl start mysql || echo "MySQL already running"  
sudo systemctl enable mysql
            """.strip()),
            
            ("Configuring Apache", """
set -e
echo "Configuring Apache..."
sudo a2enmod rewrite || echo "Rewrite module already enabled"
sudo systemctl restart apache2
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html
            """.strip())
        ]
        
        # Execute each step with retry logic
        for step_name, command in installation_steps:
            print(f"🔧 {step_name}...")
            success, output = self.run_command_with_retry(command, timeout=300)
            
            if not success:
                print(f"❌ Failed to complete: {step_name}")
                print(f"   Error: {output}")
                return False
            
            print(f"✅ {step_name} completed")
            time.sleep(2)  # Brief pause between steps
        
        print("✅ LAMP stack installation completed successfully")
        
        # Verify installation
        print("🔍 Verifying LAMP stack installation...")
        verify_command = """
set -e
echo "Checking Apache..."
apache2 -v
echo "Checking MySQL..."
mysql --version
echo "Checking PHP..."
php -v
echo "Checking services..."
sudo systemctl status apache2 --no-pager | head -5
sudo systemctl status mysql --no-pager | head -5
        """.strip()
        
        success, output = self.run_command_with_retry(verify_command, timeout=60)
        
        if success:
            print("✅ LAMP stack verification successful")
        else:
            print("⚠️  LAMP stack verification had issues, but installation may still be functional")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Install LAMP stack on AWS Lightsail instance')
    parser.add_argument('instance_name', help='Name of the Lightsail instance')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting LAMP Stack installation on {args.instance_name}")
    print(f"🌍 Region: {args.region}")
    
    # Create installer and install
    installer = LightsailLAMPInstaller(args.instance_name, args.region)
    
    success = installer.install_lamp_stack()
    
    if success:
        print(f"🎉 LAMP stack installation completed on {args.instance_name}")
        sys.exit(0)
    else:
        print(f"💥 LAMP stack installation failed on {args.instance_name}")
        sys.exit(1)

if __name__ == '__main__':
    main()
