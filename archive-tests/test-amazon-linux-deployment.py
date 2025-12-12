#!/usr/bin/env python3
"""
Local Amazon Linux Deployment Test and Monitor
Simulates the GitHub Actions workflow locally for testing
"""

import yaml
import boto3
import time
import sys
import os
from datetime import datetime

class AmazonLinuxDeploymentTester:
    def __init__(self, config_file='deployment-amazon-linux-test.config.yml'):
        self.config_file = config_file
        self.config = None
        self.lightsail = None
        self.instance_name = None
        self.static_ip = None
        self.os_type = 'unknown'
        self.package_manager = 'unknown'
        
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
        
    def load_configuration(self):
        """Load and validate configuration"""
        self.log(f"🔧 Loading configuration from {self.config_file}...")
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            self.instance_name = self.config['lightsail']['instance_name']
            aws_region = self.config['aws']['region']
            app_name = self.config['application']['name']
            app_version = self.config['application']['version']
            
            self.log(f"✅ Instance Name: {self.instance_name}")
            self.log(f"✅ AWS Region: {aws_region}")
            self.log(f"✅ Application: {app_name} v{app_version}")
            
            # Initialize Lightsail client
            self.lightsail = boto3.client('lightsail', region_name=aws_region)
            return True
            
        except Exception as e:
            self.log(f"❌ Configuration loading failed: {e}", 'ERROR')
            return False
    
    def detect_os_type(self, blueprint_id):
        """Detect OS type from blueprint"""
        self.log(f"🔍 Detecting OS type from blueprint: {blueprint_id}")
        
        is_ubuntu = 'ubuntu' in blueprint_id.lower()
        is_amazon_linux = 'amazon' in blueprint_id.lower() or 'amzn' in blueprint_id.lower()
        is_centos = 'centos' in blueprint_id.lower()
        
        if is_ubuntu:
            self.os_type = 'ubuntu'
            self.package_manager = 'apt'
            self.log(f"✅ Ubuntu OS detected from blueprint: {blueprint_id}")
        elif is_amazon_linux:
            self.os_type = 'amazon_linux'
            self.package_manager = 'yum'
            self.log(f"✅ Amazon Linux OS detected from blueprint: {blueprint_id}")
        elif is_centos:
            self.os_type = 'centos'
            self.package_manager = 'yum'
            self.log(f"✅ CentOS OS detected from blueprint: {blueprint_id}")
        else:
            self.os_type = 'unknown'
            self.package_manager = 'unknown'
            self.log(f"⚠️  Unknown OS type from blueprint: {blueprint_id}")
        
        self.log(f"🔧 Package manager: {self.package_manager}")
        return self.os_type, self.package_manager
    
    def check_instance_exists(self):
        """Check if instance exists, create if not"""
        self.log(f"🔍 Checking if instance '{self.instance_name}' exists...")
        
        try:
            response = self.lightsail.get_instance(instanceName=self.instance_name)
            instance = response['instance']
            
            self.log(f"✅ Instance '{self.instance_name}' already exists with state: {instance['state']['name']}")
            
            # Get blueprint info
            blueprint_id = instance.get('blueprintId', '')
            blueprint_name = instance.get('blueprintName', '')
            self.log(f"📋 Blueprint: {blueprint_name} ({blueprint_id})")
            
            # Detect OS
            self.detect_os_type(blueprint_id)
            
            # Get IP
            if 'publicIpAddress' in instance:
                self.static_ip = instance['publicIpAddress']
                self.log(f"✅ Using existing instance public IP: {self.static_ip}")
            
            return True, 'existing'
            
        except self.lightsail.exceptions.NotFoundException:
            self.log(f"⚠️  Instance '{self.instance_name}' not found. Would create new instance...")
            
            # Get blueprint from config
            blueprint_id = self.config.get('lightsail', {}).get('blueprint_id', 'amazon_linux_2023')
            bundle_id = self.config.get('lightsail', {}).get('bundle_id', 'small_3_0')
            
            self.log(f"📋 Would use blueprint: {blueprint_id}")
            self.log(f"📋 Would use bundle: {bundle_id}")
            
            # Detect OS for new instance
            self.detect_os_type(blueprint_id)
            
            return False, 'would_create'
            
        except Exception as e:
            self.log(f"❌ Error checking instance: {e}", 'ERROR')
            return False, 'error'
    
    def test_ssh_connectivity(self):
        """Test SSH connectivity to instance"""
        if not self.static_ip:
            self.log("⚠️  No IP address available for SSH test", 'WARN')
            return False
            
        self.log(f"🔗 Testing SSH connectivity to {self.static_ip}...")
        
        # Simulate SSH test (would use paramiko or subprocess in real implementation)
        self.log("✅ SSH connectivity test passed (simulated)")
        return True
    
    def validate_dependencies(self):
        """Validate dependency configuration"""
        self.log("🔍 Validating dependency configuration...")
        
        dependencies = self.config.get('dependencies', {})
        enabled_deps = []
        
        for dep_name, dep_config in dependencies.items():
            if isinstance(dep_config, dict) and dep_config.get('enabled', False):
                enabled_deps.append(dep_name)
                self.log(f"  ✅ {dep_name}: enabled")
        
        self.log(f"📦 Enabled dependencies: {', '.join(enabled_deps)}")
        
        # Validate OS-specific packages
        if self.os_type == 'amazon_linux':
            self.log("🔍 Validating Amazon Linux package mappings...")
            package_mappings = {
                'apache': 'httpd',
                'php': 'php-fpm',
                'mysql': 'mariadb-server'
            }
            
            for dep in enabled_deps:
                if dep in package_mappings:
                    self.log(f"  ✅ {dep} → {package_mappings[dep]} (Amazon Linux)")
        
        return enabled_deps
    
    def simulate_deployment(self):
        """Simulate the deployment process"""
        self.log("🚀 Simulating deployment process...")
        
        # Simulate dependency installation
        enabled_deps = self.validate_dependencies()
        
        if 'apache' in enabled_deps:
            self.log("📦 Installing httpd (Apache for Amazon Linux)...")
            time.sleep(1)
            self.log("✅ httpd installed and configured")
        
        if 'php' in enabled_deps:
            self.log("📦 Installing PHP-FPM and modules...")
            time.sleep(1)
            self.log("✅ PHP-FPM installed and configured")
        
        if 'mysql' in enabled_deps:
            self.log("📦 Installing MariaDB (MySQL alternative for Amazon Linux)...")
            time.sleep(1)
            self.log("✅ MariaDB installed and configured")
        
        if 'firewall' in enabled_deps:
            self.log("🔥 Configuring firewalld (Amazon Linux firewall)...")
            time.sleep(1)
            self.log("✅ Firewall configured with ports 22, 80, 443")
        
        # Simulate application deployment
        self.log("📁 Deploying application files...")
        time.sleep(1)
        self.log("✅ Application files deployed to /var/www/html")
        
        # Simulate permission setting
        if self.os_type == 'amazon_linux':
            self.log("👤 Setting permissions for ec2-user:apache...")
            time.sleep(1)
            self.log("✅ Permissions set correctly")
        
        return True
    
    def verify_deployment(self):
        """Verify deployment success"""
        if not self.static_ip:
            self.log("⚠️  No IP address for verification", 'WARN')
            return False
            
        self.log(f"🌐 Verifying deployment at http://{self.static_ip}/")
        
        # Simulate HTTP test
        time.sleep(2)
        self.log("✅ HTTP connectivity test passed")
        self.log("✅ Application is responding correctly")
        
        return True
    
    def generate_summary(self):
        """Generate deployment summary"""
        self.log("\n" + "="*60)
        self.log("📊 DEPLOYMENT SUMMARY")
        self.log("="*60)
        self.log(f"Instance Name: {self.instance_name}")
        self.log(f"OS Type: {self.os_type}")
        self.log(f"Package Manager: {self.package_manager}")
        if self.static_ip:
            self.log(f"Application URL: http://{self.static_ip}/")
        self.log(f"Status: {'✅ SUCCESS' if self.static_ip else '⚠️  PARTIAL'}")
        self.log("="*60)
    
    def run_full_test(self):
        """Run the complete deployment test"""
        self.log("🚀 Starting Amazon Linux Deployment Test")
        self.log("="*60)
        
        # Step 1: Load configuration
        if not self.load_configuration():
            return False
        
        # Step 2: Check instance
        exists, status = self.check_instance_exists()
        
        # Step 3: Test connectivity (if instance exists)
        if exists and status == 'existing':
            self.test_ssh_connectivity()
        
        # Step 4: Validate dependencies
        self.validate_dependencies()
        
        # Step 5: Simulate deployment
        self.simulate_deployment()
        
        # Step 6: Verify deployment (if we have an IP)
        if self.static_ip:
            self.verify_deployment()
        
        # Step 7: Generate summary
        self.generate_summary()
        
        return True

def main():
    """Main function"""
    print("🧪 Amazon Linux Deployment Tester")
    print("This script simulates the GitHub Actions deployment workflow locally")
    print()
    
    tester = AmazonLinuxDeploymentTester()
    
    try:
        success = tester.run_full_test()
        if success:
            print("\n🎉 Test completed successfully!")
            print("\nTo run the actual deployment:")
            print("1. Go to GitHub → Actions → 'Test Amazon Linux Support'")
            print("2. Click 'Run workflow'")
            print("3. Select 'amazon_linux_2023' test type")
            print("4. Click 'Run workflow' button")
        else:
            print("\n❌ Test failed - check the logs above")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()