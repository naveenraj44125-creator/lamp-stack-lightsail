#!/usr/bin/env python3
"""
Clear old command logs and test new logging format
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lightsail_common import LightsailBase

def clear_and_test_logs():
    """Clear old logs and test new logging format"""
    
    print("🧹 Clearing Old Command Logs and Testing New Format")
    print("=" * 60)
    
    # Get instance name from environment or use default
    instance_name = os.environ.get('LIGHTSAIL_INSTANCE_NAME', 'lamp-stack-instance')
    
    try:
        # Create client
        client = LightsailBase(instance_name, "us-east-1")
        
        print(f"🔍 Connecting to instance: {instance_name}")
        
        # Test connectivity first
        print("\n📡 Testing connectivity...")
        success, _ = client.run_command("echo 'Connection test successful'", timeout=30, max_retries=1)
        
        if not success:
            print("❌ Cannot connect to instance. Please check:")
            print("   • Instance is running")
            print("   • Instance name is correct")
            print("   • AWS credentials are configured")
            return False
        
        print("✅ Connection successful!")
        
        # Clear old command logs
        print("\n🧹 Clearing old command logs...")
        success, output = client.clear_command_log()
        
        if success:
            print("✅ Old command logs cleared")
        else:
            print(f"⚠️ Could not clear logs: {output}")
        
        # Test new logging format with a few commands
        print("\n🧪 Testing new logging format...")
        
        # Test 1: Simple command
        print("\n📋 Test 1: Simple command")
        success, _ = client.run_command("echo 'Testing new logging format - simple command'", timeout=30)
        
        # Test 2: Multi-line script
        print("\n📋 Test 2: Multi-line script")
        test_script = """set -e
echo "Testing multi-line script logging"

# This is a test script
echo "Step 1: Creating test directory"
mkdir -p /tmp/test_logging

echo "Step 2: Writing test file"
echo "Test content" > /tmp/test_logging/test.txt

echo "✅ Multi-line script test completed"
"""
        success, _ = client.run_command(test_script, timeout=60)
        
        # Test 3: Another simple command
        print("\n📋 Test 3: Another simple command")
        success, _ = client.run_command("ls -la /tmp/test_logging/", timeout=30)
        
        # Now show the new log format
        print("\n📋 Retrieving new command logs...")
        success, log_content = client.get_command_log(lines=10)
        
        if success and log_content != "No commands logged yet":
            print("\n🎯 NEW LOG FORMAT:")
            print("-" * 50)
            print(log_content)
            print("-" * 50)
            
            # Check if we still see pipes
            if " | " in log_content:
                print("\n⚠️ Still seeing pipes in logs - this might be from old entries")
            else:
                print("\n✅ No more pipe symbols! New logging format is working!")
        else:
            print(f"\n⚠️ Could not retrieve logs: {log_content}")
        
        # Clean up test files
        print("\n🧹 Cleaning up test files...")
        client.run_command("rm -rf /tmp/test_logging", timeout=30)
        
        print("\n✅ Log clearing and testing completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Set GitHub Actions environment for enhanced logging
    os.environ['GITHUB_ACTIONS'] = 'true'
    
    success = clear_and_test_logs()
    sys.exit(0 if success else 1)