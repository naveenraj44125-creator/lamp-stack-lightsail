#!/usr/bin/env python3
"""
Test script to demonstrate detailed command logging
"""

import os
import sys
from lightsail_common import LightsailBase
from config_loader import DeploymentConfig

def test_detailed_logging():
    """Test the detailed logging functionality"""
    
    # Set GitHub Actions environment for verbose logging
    os.environ['GITHUB_ACTIONS'] = 'true'
    
    try:
        # Load configuration
        config = DeploymentConfig()
        instance_name = config.get_instance_name()
        region = config.get_aws_region()
        
        print("="*80)
        print("🧪 TESTING DETAILED COMMAND LOGGING")
        print("="*80)
        print(f"🌍 Instance: {instance_name}")
        print(f"📍 Region: {region}")
        
        # Create client
        client = LightsailBase(instance_name, region)
        
        # Test 1: Simple command with verbose output
        print("\n" + "="*60)
        print("🧪 TEST 1: Simple Command with Verbose Output")
        print("="*60)
        
        simple_command = "echo 'Testing simple command'; whoami; pwd; date"
        success, output = client.run_command(simple_command, verbose=True)
        
        if success:
            print("✅ Test 1 passed")
        else:
            print("❌ Test 1 failed")
        
        # Test 2: Complex script with individual command breakdown
        print("\n" + "="*60)
        print("🧪 TEST 2: Complex Script with Command Breakdown")
        print("="*60)
        
        complex_script = '''
set -e
echo "Starting complex script test..."

# Update package list
sudo apt-get update -qq

# Check system information
echo "System Information:"
uname -a
df -h /
free -h

# Check installed packages
echo "Checking for Apache..."
if systemctl is-active --quiet apache2; then
    echo "✅ Apache is running"
    systemctl status apache2 --no-pager -l | head -3
else
    echo "ℹ️  Apache is not running"
fi

echo "✅ Complex script test completed"
'''
        
        success, output = client.run_command_with_live_output(complex_script)
        
        if success:
            print("✅ Test 2 passed")
        else:
            print("❌ Test 2 failed")
        
        # Test 3: MySQL commands with detailed output
        print("\n" + "="*60)
        print("🧪 TEST 3: Database Commands with Detailed Output")
        print("="*60)
        
        mysql_script = '''
set -e
echo "Testing MySQL connectivity..."

# Check if MySQL is installed
if command -v mysql >/dev/null 2>&1; then
    echo "✅ MySQL client found"
    
    # Test connection
    if mysql -u root -proot123 -e "SELECT VERSION() as mysql_version, NOW() as current_time;" 2>/dev/null; then
        echo "✅ MySQL connection successful"
        
        # Show databases
        echo "Available databases:"
        mysql -u root -proot123 -e "SHOW DATABASES;" 2>/dev/null
        
        # Test app database
        if mysql -u root -proot123 -e "USE app_db; SELECT COUNT(*) as record_count FROM test_table;" 2>/dev/null; then
            echo "✅ Application database test successful"
        else
            echo "⚠️  Application database test failed"
        fi
    else
        echo "❌ MySQL connection failed"
    fi
else
    echo "ℹ️  MySQL client not installed"
fi

echo "✅ Database test completed"
'''
        
        success, output = client.run_command_with_live_output(mysql_script)
        
        if success:
            print("✅ Test 3 passed")
        else:
            print("❌ Test 3 failed")
        
        print("\n" + "="*80)
        print("🎉 DETAILED LOGGING TESTS COMPLETED")
        print("="*80)
        print("💡 This demonstrates how each command will be logged in GitHub Actions")
        print("📋 Each individual command is shown with its output")
        print("🔍 Errors are displayed with detailed context")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    test_detailed_logging()