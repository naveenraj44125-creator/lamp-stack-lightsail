#!/usr/bin/env python3
"""
LAMP Stack Deployment Script for AWS Lightsail
Uses run_commands to deploy the application instead of user_data
"""

import boto3
import json
import time
import sys
import os
from botocore.exceptions import ClientError, NoCredentialsError

class LightsailDeployer:
    def __init__(self, instance_name="lamp-stack-demo", region="us-east-1"):
        self.instance_name = instance_name
        self.region = region
        try:
            self.lightsail = boto3.client('lightsail', region_name=region)
            print(f"✓ AWS Lightsail client initialized for region: {region}")
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure your credentials.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error initializing AWS client: {e}")
            sys.exit(1)

    def wait_for_instance_running(self, timeout=300):
        """Wait for the instance to be in running state"""
        print(f"⏳ Waiting for instance '{self.instance_name}' to be running...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.lightsail.get_instance(instanceName=self.instance_name)
                state = response['instance']['state']['name']
                print(f"   Instance state: {state}")
                
                if state == 'running':
                    print("✓ Instance is running!")
                    return True
                elif state in ['stopped', 'stopping', 'terminated']:
                    print(f"❌ Instance is in {state} state")
                    return False
                    
                time.sleep(10)
            except ClientError as e:
                if e.response['Error']['Code'] == 'NotFoundException':
                    print(f"❌ Instance '{self.instance_name}' not found")
                    return False
                print(f"⚠️  Error checking instance state: {e}")
                time.sleep(10)
        
        print(f"❌ Timeout waiting for instance to be running")
        return False

    def run_command(self, command, description=""):
        """Execute a command on the Lightsail instance"""
        if description:
            print(f"🔧 {description}")
        
        print(f"   Running: {command}")
        
        try:
            response = self.lightsail.send_command(
                instanceName=self.instance_name,
                command=command
            )
            
            operation_id = response['operations'][0]['id']
            print(f"   Operation ID: {operation_id}")
            
            # Wait for command completion
            return self.wait_for_operation(operation_id)
            
        except ClientError as e:
            print(f"❌ Error running command: {e}")
            return False

    def wait_for_operation(self, operation_id, timeout=300):
        """Wait for a Lightsail operation to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.lightsail.get_operation(operationId=operation_id)
                status = response['operation']['status']
                
                if status == 'Succeeded':
                    print("   ✓ Command completed successfully")
                    return True
                elif status == 'Failed':
                    print("   ❌ Command failed")
                    if 'statusChangedAt' in response['operation']:
                        print(f"   Error details: {response['operation']}")
                    return False
                elif status in ['Started', 'Completed']:
                    time.sleep(2)
                else:
                    print(f"   Status: {status}")
                    time.sleep(5)
                    
            except ClientError as e:
                print(f"   ⚠️  Error checking operation: {e}")
                time.sleep(5)
        
        print("   ❌ Timeout waiting for operation")
        return False

    def install_lamp_stack(self):
        """Install and configure LAMP stack components"""
        commands = [
            {
                "command": "sudo apt update && sudo apt upgrade -y",
                "description": "Updating system packages"
            },
            {
                "command": "sudo apt install -y apache2 mysql-server php php-mysql php-cli php-curl php-gd php-mbstring php-xml php-zip unzip curl wget",
                "description": "Installing LAMP stack components"
            },
            {
                "command": "sudo systemctl enable apache2 && sudo systemctl start apache2",
                "description": "Starting and enabling Apache"
            },
            {
                "command": "sudo systemctl enable mysql && sudo systemctl start mysql",
                "description": "Starting and enabling MySQL"
            },
            {
                "command": "sudo mysql -e \"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'rootpassword123';\"",
                "description": "Setting MySQL root password"
            },
            {
                "command": "sudo mysql -e \"CREATE DATABASE IF NOT EXISTS lamp_app;\"",
                "description": "Creating application database"
            },
            {
                "command": "sudo mysql -e \"CREATE USER IF NOT EXISTS 'lampuser'@'localhost' IDENTIFIED BY 'lamppass123';\"",
                "description": "Creating database user"
            },
            {
                "command": "sudo mysql -e \"GRANT ALL PRIVILEGES ON lamp_app.* TO 'lampuser'@'localhost'; FLUSH PRIVILEGES;\"",
                "description": "Granting database privileges"
            }
        ]
        
        for cmd in commands:
            if not self.run_command(cmd["command"], cmd["description"]):
                return False
        
        return True

    def configure_apache(self):
        """Configure Apache web server"""
        commands = [
            {
                "command": "sudo a2enmod rewrite",
                "description": "Enabling Apache rewrite module"
            },
            {
                "command": "sudo chown -R www-data:www-data /var/www/html",
                "description": "Setting proper ownership for web directory"
            },
            {
                "command": "sudo chmod -R 755 /var/www/html",
                "description": "Setting proper permissions for web directory"
            }
        ]
        
        for cmd in commands:
            if not self.run_command(cmd["command"], cmd["description"]):
                return False
        
        return True

    def deploy_application(self):
        """Deploy the LAMP application files"""
        # Create application files using heredoc
        index_php_content = '''<?php
// LAMP Stack Demo Application
// Database configuration
$host = 'localhost';
$dbname = 'lamp_app';
$username = 'lampuser';
$password = 'lamppass123';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db_status = "✓ Database Connected Successfully";
    $db_class = "success";
} catch(PDOException $e) {
    $db_status = "❌ Database Connection Failed: " . $e->getMessage();
    $db_class = "error";
}

// Get system information
$php_version = phpversion();
$server_software = $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown';
$current_time = date('Y-m-d H:i:s T');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LAMP Stack Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
            width: 100%;
            animation: fadeInUp 0.8s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 300;
        }
        
        .welcome-message {
            font-size: 1.5em;
            color: #555;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border-radius: 10px;
            font-weight: 500;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .info-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .info-card h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .info-card p {
            color: #666;
            font-size: 0.9em;
        }
        
        .status.success {
            color: #28a745;
            font-weight: bold;
        }
        
        .status.error {
            color: #dc3545;
            font-weight: bold;
        }
        
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #888;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 10px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .welcome-message {
                font-size: 1.2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 LAMP Stack Demo</h1>
        
        <div class="welcome-message">
            Hello Welcome! 👋
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>🐘 PHP Version</h3>
                <p><?php echo $php_version; ?></p>
            </div>
            
            <div class="info-card">
                <h3>🌐 Web Server</h3>
                <p><?php echo $server_software; ?></p>
            </div>
            
            <div class="info-card">
                <h3>🗄️ Database Status</h3>
                <p class="status <?php echo $db_class; ?>"><?php echo $db_status; ?></p>
            </div>
            
            <div class="info-card">
                <h3>⏰ Current Time</h3>
                <p><?php echo $current_time; ?></p>
            </div>
        </div>
        
        <div class="footer">
            <p>LAMP Stack (Linux + Apache + MySQL + PHP) deployed on AWS Lightsail</p>
            <p>Deployed via GitHub Actions with run_commands</p>
        </div>
    </div>
</body>
</html>'''

        # Deploy the application
        commands = [
            {
                "command": "sudo rm -f /var/www/html/index.html",
                "description": "Removing default Apache page"
            },
            {
                "command": f"sudo tee /var/www/html/index.php > /dev/null << 'EOF'\n{index_php_content}\nEOF",
                "description": "Creating main application file"
            },
            {
                "command": "sudo chown www-data:www-data /var/www/html/index.php",
                "description": "Setting proper ownership for application files"
            },
            {
                "command": "sudo chmod 644 /var/www/html/index.php",
                "description": "Setting proper permissions for application files"
            },
            {
                "command": "sudo systemctl restart apache2",
                "description": "Restarting Apache to apply changes"
            }
        ]
        
        for cmd in commands:
            if not self.run_command(cmd["command"], cmd["description"]):
                return False
        
        return True

    def verify_deployment(self):
        """Verify that the deployment was successful"""
        commands = [
            {
                "command": "curl -s -o /dev/null -w '%{http_code}' http://localhost/",
                "description": "Testing web server response"
            },
            {
                "command": "sudo systemctl is-active apache2",
                "description": "Checking Apache status"
            },
            {
                "command": "sudo systemctl is-active mysql",
                "description": "Checking MySQL status"
            }
        ]
        
        for cmd in commands:
            if not self.run_command(cmd["command"], cmd["description"]):
                print(f"⚠️  Verification step failed: {cmd['description']}")
        
        return True

    def get_instance_info(self):
        """Get and display instance information"""
        try:
            response = self.lightsail.get_instance(instanceName=self.instance_name)
            instance = response['instance']
            
            print("\n" + "="*50)
            print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("="*50)
            print(f"Instance Name: {instance['name']}")
            print(f"Public IP: {instance.get('publicIpAddress', 'N/A')}")
            print(f"Private IP: {instance.get('privateIpAddress', 'N/A')}")
            print(f"State: {instance['state']['name']}")
            print(f"Blueprint: {instance['blueprintName']}")
            print(f"Bundle: {instance['bundleName']}")
            
            # Try to get static IP
            try:
                static_ips = self.lightsail.get_static_ips()
                for static_ip in static_ips['staticIps']:
                    if static_ip.get('attachedTo') == self.instance_name:
                        print(f"Static IP: {static_ip['ipAddress']}")
                        print(f"\n🌐 Access your application at: http://{static_ip['ipAddress']}")
                        break
                else:
                    if instance.get('publicIpAddress'):
                        print(f"\n🌐 Access your application at: http://{instance['publicIpAddress']}")
            except:
                if instance.get('publicIpAddress'):
                    print(f"\n🌐 Access your application at: http://{instance['publicIpAddress']}")
            
            print("\n📋 Application Features:")
            print("  • LAMP Stack (Linux + Apache + MySQL + PHP)")
            print("  • Responsive web interface")
            print("  • Database connectivity test")
            print("  • System information display")
            print("  • Mobile-friendly design")
            
        except ClientError as e:
            print(f"❌ Error getting instance info: {e}")

    def deploy(self):
        """Main deployment function"""
        print("🚀 Starting LAMP Stack deployment...")
        print(f"Target instance: {self.instance_name}")
        print(f"Region: {self.region}")
        
        # Wait for instance to be running
        if not self.wait_for_instance_running():
            print("❌ Instance is not running. Please check your Terraform deployment.")
            return False
        
        # Install LAMP stack
        print("\n📦 Installing LAMP stack components...")
        if not self.install_lamp_stack():
            print("❌ Failed to install LAMP stack")
            return False
        
        # Configure Apache
        print("\n⚙️  Configuring Apache web server...")
        if not self.configure_apache():
            print("❌ Failed to configure Apache")
            return False
        
        # Deploy application
        print("\n🎯 Deploying application files...")
        if not self.deploy_application():
            print("❌ Failed to deploy application")
            return False
        
        # Verify deployment
        print("\n✅ Verifying deployment...")
        self.verify_deployment()
        
        # Show instance info
        self.get_instance_info()
        
        return True

def main():
    """Main function"""
    # Get instance name from environment or use default
    instance_name = os.environ.get('INSTANCE_NAME', 'lamp-stack-demo')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    
    print("LAMP Stack Lightsail Deployment Script")
    print("=====================================")
    
    deployer = LightsailDeployer(instance_name, region)
    
    if deployer.deploy():
        print("\n🎉 Deployment completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
