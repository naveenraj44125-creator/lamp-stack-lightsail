#!/usr/bin/env python3
"""
Test script to demonstrate exact command logging to Lightsail host
"""

import os
import sys
from lightsail_common import LightsailBase
from config_loader import DeploymentConfig

def main():
    """Test command logging"""
    
    # Set GitHub Actions environment for enhanced logging
    os.environ['GITHUB_ACTIONS'] = 'true'
    
    try:
        # Load configuration
        config = DeploymentConfig()
        instance_name = config.get_instance_name()
        region = config.get_aws_region()
        
        print("="*80)
        print("🧪 TESTING EXACT COMMAND LOGGING TO LIGHTSAIL HOST")
        print("="*80)
        print(f"🌍 Instance: {instance_name}")
        print(f"📍 Region: {region}")
        
        # Create client
        client = LightsailBase(instance_name, region)
        
        # Test 1: Simple single command
        print("\n🧪 TEST 1: Simple single command")
        print("="*50)
        
        simple_cmd = "echo 'Hello from Lightsail host!'"
        success, output = client.run_command(simple_cmd)
        
        # Test 2: Multiple individual commands
        print("\n🧪 TEST 2: Multiple individual commands")
        print("="*50)
        
        commands = [
            "whoami",
            "pwd", 
            "date",
            "uname -a",
            "df -h /"
        ]
        
        for i, cmd in enumerate(commands, 1):
            print(f"\n--- Command {i}/{len(commands)} ---")
            success, output = client.run_command(cmd)
            if not success:
                print(f"Command {i} failed!")
        
        # Test 3: System information commands
        print("\n🧪 TEST 3: System information commands")
        print("="*50)
        
        system_cmd = "echo 'System Information:'; cat /etc/os-release | head -5"
        success, output = client.run_command(system_cmd)
        
        # Test 4: Service status commands
        print("\n🧪 TEST 4: Service status commands")
        print("="*50)
        
        service_cmd = "systemctl status apache2 --no-pager -l | head -10 || echo 'Apache not running'"
        success, output = client.run_command(service_cmd)
        
        # Test 5: Database commands
        print("\n🧪 TEST 5: Database commands")
        print("="*50)
        
        db_cmd = "mysql -u root -proot123 -e 'SHOW DATABASES;' 2>/dev/null || echo 'MySQL not configured'"
        success, output = client.run_command(db_cmd)
        
        print("\n" + "="*80)
        print("🎉 COMMAND LOGGING TESTS COMPLETED")
        print("="*80)
        print("💡 Each command above was sent individually to the Lightsail host")
        print("📋 You can see the exact command and its output")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()