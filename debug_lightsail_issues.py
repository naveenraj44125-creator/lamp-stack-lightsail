#!/usr/bin/env python3

"""
Debug Lightsail Issues
=====================
Debug the MySQL RDS and PHP installation issues found in the GitHub Actions workflow.
"""

import boto3
import subprocess
import tempfile
import os
import time
import sys

class LightsailDebugger:
    def __init__(self, instance_name, region="us-east-1"):
        self.lightsail = boto3.client('lightsail', region_name=region)
        self.region = region
        self.instance_name = instance_name
        self.instance_ip = None
        
    def create_ssh_files(self, ssh_details):
        """Create temporary SSH key files using get_instance_access_details"""
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
            print(f"🔧 [{self.instance_name}] {command[:100]}{'...' if len(command) > 100 else ''}")
            
            ssh_response = self.lightsail.get_instance_access_details(instanceName=self.instance_name)
            ssh_details = ssh_response['accessDetails']
            
            # Store instance IP for later use
            if not self.instance_ip:
                self.instance_ip = ssh_details['ipAddress']
            
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
                        # Show output
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
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

    def debug_php_installation(self):
        """Debug PHP installation issues"""
        print(f"\n🔍 Debugging PHP Installation Issues...")
        
        debug_commands = [
            # Check Ubuntu version
            "lsb_release -a",
            
            # Check available PHP packages
            "apt list --available | grep php8.1 | head -10",
            
            # Check if ondrej/php PPA is needed
            "apt-cache policy | grep php",
            
            # Check current PHP installation
            "php --version 2>/dev/null || echo 'PHP not installed'",
            
            # Check what PHP packages are available
            "apt search php | grep php8 | head -10",
            
            # Try to add ondrej/php repository
            "sudo apt update && sudo apt install -y software-properties-common",
            "sudo add-apt-repository ppa:ondrej/php -y",
            "sudo apt update",
            
            # Check PHP packages after adding PPA
            "apt list --available | grep php8.1 | head -10",
        ]
        
        for cmd in debug_commands:
            success, output = self.run_command_on_instance(cmd)
            print()  # Add spacing between commands

    def debug_mysql_rds_config(self):
        """Debug MySQL RDS configuration issues"""
        print(f"\n🔍 Debugging MySQL RDS Configuration Issues...")
        
        debug_commands = [
            # Check the lightsail_rds.py file for the error
            "ls -la /tmp/",
            
            # Check if there are any Python files with RDS configuration
            "find /var/www/html -name '*.py' -exec grep -l 'access_key' {} \\; 2>/dev/null || echo 'No Python files with access_key found'",
            
            # Check the deployment scripts
            "find /tmp -name '*.py' -exec grep -l 'access_key' {} \\; 2>/dev/null || echo 'No deployment scripts with access_key found'",
            
            # Check MySQL client installation
            "mysql --version 2>/dev/null || echo 'MySQL client not installed'",
            
            # Check if we can connect to RDS (this will likely fail but shows the error)
            "mysql -h ls-64e1bfa3e7e830b55b522ced46f63beaf9e8e046.cnhasnqdqfjq.us-east-1.rds.amazonaws.com -u admin -p'SecurePass123!' -e 'SELECT 1;' 2>&1 || echo 'RDS connection test completed'",
        ]
        
        for cmd in debug_commands:
            success, output = self.run_command_on_instance(cmd)
            print()  # Add spacing between commands

    def check_current_application_status(self):
        """Check the current status of the application"""
        print(f"\n🔍 Checking Current Application Status...")
        
        status_commands = [
            # Check Apache status
            "sudo systemctl status apache2 --no-pager",
            
            # Check what's in the web directory
            "ls -la /var/www/html/",
            
            # Check if the application is accessible
            "curl -s -o /dev/null -w '%{http_code}' http://localhost/ || echo 'Local HTTP test failed'",
            
            # Check Apache error logs
            "sudo tail -20 /var/log/apache2/error.log",
            
            # Check what processes are running
            "ps aux | grep -E '(apache|mysql|php)' | grep -v grep",
        ]
        
        for cmd in status_commands:
            success, output = self.run_command_on_instance(cmd)
            print()  # Add spacing between commands

    def run_full_debug(self):
        """Run complete debugging session"""
        print("🎯 LIGHTSAIL DEBUGGING SESSION")
        print("="*50)
        
        try:
            # Check current application status
            self.check_current_application_status()
            
            # Debug PHP installation issues
            self.debug_php_installation()
            
            # Debug MySQL RDS configuration
            self.debug_mysql_rds_config()
            
            print("\n" + "="*50)
            print("🎉 DEBUGGING SESSION COMPLETED!")
            print("="*50)
            
            if self.instance_ip:
                print(f"✅ Instance IP: {self.instance_ip}")
                print(f"✅ You can test the application at: http://{self.instance_ip}/")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Debugging failed: {str(e)}")
            return False

def main():
    """Main function"""
    instance_name = "lamp-stack-demo"
    
    debugger = LightsailDebugger(instance_name)
    success = debugger.run_full_debug()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
