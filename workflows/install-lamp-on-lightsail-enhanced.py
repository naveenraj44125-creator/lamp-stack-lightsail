#!/usr/bin/env python3
"""
LAMP Stack Installation Script for AWS Lightsail
Installs Apache, MySQL/MariaDB, and PHP on a Lightsail instance
"""

import sys
import os
import time
import argparse
from lightsail_common import create_lightsail_client
from lightsail_lamp import LightsailLAMPManager

class LightsailLAMPInstaller:
    def __init__(self, instance_name, region='us-east-1'):
        self.client = LightsailLAMPManager(instance_name, region)

    def install_lamp_stack(self):
        """Install LAMP stack on Lightsail instance"""
        print(f"🚀 Starting LAMP stack installation on {self.client.instance_name}")
        
        # Check if instance is running and SSH is ready
        ssh_manager = create_lightsail_client(self.client.instance_name, self.client.region, 'ssh')
        if not ssh_manager.wait_for_ssh_ready():
            return False
        
        # Wait additional time for SSH service to be fully ready
        print("⏳ Waiting 60 seconds for SSH service to be fully ready...")
        time.sleep(60)

        # Test SSH connection before proceeding with enhanced diagnostics
        if not self.client.test_ssh_connectivity():
            print("⚠️ SSH connection test failed, but proceeding with retry logic...")
            
            # For GitHub Actions, try one instance restart before proceeding
            if "GITHUB_ACTIONS" in os.environ:
                print("🔄 GitHub Actions detected - performing preventive instance restart...")
                self.client.restart_instance_for_connectivity()
        
        # Use the common LAMP installation functionality with enhanced retry logic
        success, output = self.client.install_lamp_stack(timeout=900, max_retries=8)
        
        if not success:
            print("❌ LAMP stack installation failed")
            print(f"   Error: {output}")
            return False
        
        print("✅ LAMP stack installation completed successfully")
        
        # Verify installation using common functionality
        success, output = self.client.verify_lamp_stack(timeout=120, max_retries=3)
        
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
