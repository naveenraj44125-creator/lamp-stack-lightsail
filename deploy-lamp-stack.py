#!/usr/bin/env python3
"""
LAMP Stack Deployment Script for AWS Lightsail
Deploys application code to a pre-existing Lightsail instance via SSH
"""

import boto3
import paramiko
import time
import sys
import os
import argparse
from datetime import datetime

def run_ssh_command(ssh_client, command, timeout=300):
    """Execute a command via SSH and return the result"""
    try:
        print(f"Executing: {command}")
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
        
        # Wait for command to complete
        exit_status = stdout.channel.recv_exit_status()
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if exit_status == 0:
            print(f"✅ Command successful")
            if output.strip():
                print(f"Output: {output.strip()}")
        else:
            print(f"❌ Command failed with exit status {exit_status}")
            if error.strip():
                print(f"Error: {error.strip()}")
            if output.strip():
                print(f"Output: {output.strip()}")
        
        return exit_status == 0, output, error
    except Exception as e:
        print(f"❌ SSH command failed: {str(e)}")
        return False, "", str(e)

def wait_for_ssh(instance_ip, ssh_key_path, ssh_user="ubuntu", max_attempts=30):
    """Wait for SSH to become available"""
    print(f"🔄 Waiting for SSH connection to {instance_ip}...")
    
    for attempt in range(max_attempts):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh_client.connect(
                hostname=instance_ip,
                username=ssh_user,
                key_filename=ssh_key_path,
                timeout=10
            )
            
            # Test connection with a simple command
            success, _, _ = run_ssh_command(ssh_client, "echo 'SSH connection successful'")
            if success:
                print(f"✅ SSH connection established!")
                return ssh_client
            
            ssh_client.close()
            
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_attempts}: SSH not ready yet ({str(e)})")
            time.sleep(10)
    
    raise Exception(f"Failed to establish SSH connection after {max_attempts} attempts")

def install_lamp_stack(ssh_client):
    """Install LAMP stack on the instance"""
    print("🔧 Installing LAMP stack...")
    
    commands = [
        # Update system
        "sudo apt update -y",
        
        # Install Apache
        "sudo apt install -y apache2",
        "sudo systemctl enable apache2",
        "sudo systemctl start apache2",
        
        # Install MySQL
        "sudo apt install -y mysql-server",
        "sudo systemctl enable mysql",
        "sudo systemctl start mysql",
        
        # Install PHP
        "sudo apt install -y php libapache2-mod-php php-mysql php-cli php-curl php-json php-mbstring",
        
        # Configure Apache for PHP
        "sudo a2enmod php8.1",
        "sudo systemctl restart apache2",
        
        # Set up MySQL database
        """sudo mysql -e "CREATE DATABASE IF NOT EXISTS lamp_demo;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'lamp_user'@'localhost' IDENTIFIED BY 'lamp_password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON lamp_demo.* TO 'lamp_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"
sudo mysql -e "USE lamp_demo; CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50) NOT NULL, email VARCHAR(100) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
sudo mysql -e "USE lamp_demo; INSERT IGNORE INTO users (username, email) VALUES ('demo_user', 'demo@example.com'), ('test_user', 'test@example.com');"
""",
        
        # Set proper permissions
        "sudo chown -R www-data:www-data /var/www/html",
        "sudo chmod -R 755 /var/www/html",
    ]
    
    for command in commands:
        success, output, error = run_ssh_command(ssh_client, command, timeout=600)
        if not success:
            print(f"❌ Failed to execute: {command}")
            print(f"Error: {error}")
            return False
    
    print("✅ LAMP stack installation completed!")
    return True

def deploy_application(ssh_client, app_files, github_info=None):
    """Deploy application files to the instance"""
    print("📦 Deploying application files...")
    
    # Create deployment info
    deploy_info = {
        'deploy_time': datetime.utcnow().isoformat() + 'Z',
        'github_sha': github_info.get('sha', 'unknown') if github_info else 'local',
        'github_ref': github_info.get('ref', 'unknown') if github_info else 'local',
        'github_actor': github_info.get('actor', 'unknown') if github_info else 'local',
        'github_run_id': github_info.get('run_id', 'unknown') if github_info else 'local'
    }
    
    # Remove default Apache index file
    success, _, _ = run_ssh_command(ssh_client, "sudo rm -f /var/www/html/index.html")
    
    # Create deployment info file
    deploy_info_content = f"""<?php
// Deployment Information
define('DEPLOY_TIME', '{deploy_info['deploy_time']}');
define('GITHUB_SHA', '{deploy_info['github_sha']}');
define('GITHUB_REF', '{deploy_info['github_ref']}');
define('GITHUB_ACTOR', '{deploy_info['github_actor']}');
define('GITHUB_RUN_ID', '{deploy_info['github_run_id']}');
?>"""
    
    # Upload deployment info
    success, _, _ = run_ssh_command(ssh_client, f"sudo tee /var/www/html/deploy_info.php > /dev/null << 'EOF'\n{deploy_info_content}\nEOF")
    
    # Upload application files using SFTP
    try:
        sftp = ssh_client.open_sftp()
        
        # Upload files based on app_files parameter
        files_to_upload = app_files.split(',') if isinstance(app_files, str) else app_files
        
        for file_path in files_to_upload:
            file_path = file_path.strip()
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    # Upload single file
                    remote_path = f"/tmp/{os.path.basename(file_path)}"
                    print(f"Uploading {file_path} to {remote_path}")
                    sftp.put(file_path, remote_path)
                    
                    # Move to web directory with proper permissions
                    run_ssh_command(ssh_client, f"sudo cp {remote_path} /var/www/html/")
                    run_ssh_command(ssh_client, f"rm {remote_path}")
                    
                elif os.path.isdir(file_path):
                    # Upload directory recursively
                    for root, dirs, files in os.walk(file_path):
                        for file in files:
                            local_file = os.path.join(root, file)
                            relative_path = os.path.relpath(local_file, '.')
                            remote_path = f"/tmp/{relative_path.replace(os.sep, '_')}"
                            
                            print(f"Uploading {local_file} to {remote_path}")
                            sftp.put(local_file, remote_path)
                            
                            # Create directory structure and move file
                            remote_dir = f"/var/www/html/{os.path.dirname(relative_path)}"
                            run_ssh_command(ssh_client, f"sudo mkdir -p {remote_dir}")
                            run_ssh_command(ssh_client, f"sudo cp {remote_path} /var/www/html/{relative_path}")
                            run_ssh_command(ssh_client, f"rm {remote_path}")
        
        sftp.close()
        
    except Exception as e:
        print(f"❌ SFTP upload failed: {str(e)}")
        return False
    
    # Set proper permissions
    run_ssh_command(ssh_client, "sudo chown -R www-data:www-data /var/www/html")
    run_ssh_command(ssh_client, "sudo chmod -R 755 /var/www/html")
    
    # Restart Apache to ensure changes take effect
    run_ssh_command(ssh_client, "sudo systemctl restart apache2")
    
    print("✅ Application deployment completed!")
    return True

def verify_deployment(ssh_client, instance_ip):
    """Verify that the deployment was successful"""
    print("🔍 Verifying deployment...")
    
    # Check Apache status
    success, output, _ = run_ssh_command(ssh_client, "sudo systemctl is-active apache2")
    if not success or "active" not in output:
        print("❌ Apache is not running")
        return False
    
    # Check MySQL status
    success, output, _ = run_ssh_command(ssh_client, "sudo systemctl is-active mysql")
    if not success or "active" not in output:
        print("❌ MySQL is not running")
        return False
    
    # Check if application files exist
    success, _, _ = run_ssh_command(ssh_client, "ls -la /var/www/html/index.php")
    if not success:
        print("❌ Application files not found")
        return False
    
    # Test web server response
    success, output, _ = run_ssh_command(ssh_client, f"curl -s http://localhost/ | head -20")
    if success and "Hello Welcome" in output:
        print("✅ Web application is responding correctly!")
        print(f"🌐 Application URL: http://{instance_ip}/")
        return True
    else:
        print("❌ Web application is not responding correctly")
        print(f"Response: {output}")
        return False

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Deploy LAMP stack application to Lightsail')
    parser.add_argument('--instance-ip', required=True, help='IP address of the Lightsail instance')
    parser.add_argument('--ssh-key', required=True, help='Path to SSH private key file')
    parser.add_argument('--ssh-user', default='ubuntu', help='SSH username (default: ubuntu)')
    parser.add_argument('--app-files', required=True, help='Comma-separated list of files/directories to deploy')
    parser.add_argument('--github-sha', help='GitHub commit SHA')
    parser.add_argument('--github-ref', help='GitHub branch/ref name')
    parser.add_argument('--github-actor', help='GitHub actor (user who triggered the action)')
    parser.add_argument('--github-run-id', help='GitHub Actions run ID')
    parser.add_argument('--skip-lamp-install', action='store_true', help='Skip LAMP stack installation')
    
    return parser.parse_args()

def main():
    """Main deployment function"""
    args = parse_arguments()
    
    # Prepare GitHub info
    github_info = {
        'sha': args.github_sha,
        'ref': args.github_ref,
        'actor': args.github_actor,
        'run_id': args.github_run_id
    } if args.github_sha else None
    
    print("🚀 Starting LAMP Stack deployment...")
    print(f"Target instance: {args.instance_ip}")
    print(f"SSH key: {args.ssh_key}")
    print(f"App files: {args.app_files}")
    
    if github_info:
        print(f"GitHub SHA: {github_info['sha']}")
        print(f"GitHub Ref: {github_info['ref']}")
        print(f"GitHub Actor: {github_info['actor']}")
    
    try:
        # Wait for SSH to be available
        ssh_client = wait_for_ssh(args.instance_ip, args.ssh_key, args.ssh_user)
        
        # Install LAMP stack (unless skipped)
        if not args.skip_lamp_install:
            if not install_lamp_stack(ssh_client):
                print("❌ LAMP stack installation failed")
                return False
        else:
            print("⏭️  Skipping LAMP stack installation")
        
        # Deploy application
        if not deploy_application(ssh_client, args.app_files, github_info):
            print("❌ Application deployment failed")
            return False
        
        # Verify deployment
        if not verify_deployment(ssh_client, args.instance_ip):
            print("❌ Deployment verification failed")
            return False
        
        ssh_client.close()
        
        print("🎉 Deployment completed successfully!")
        print(f"🌐 Application URL: http://{args.instance_ip}/")
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
