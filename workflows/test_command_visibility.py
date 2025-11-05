#!/usr/bin/env python3
"""
Test script to verify command logging visibility in GitHub Actions
This will send individual commands to the Lightsail host and show exactly what gets logged
"""

import os
import sys
from lightsail_common import create_lightsail_client

def test_individual_commands():
    """Test sending individual commands to see logging output"""
    
    # Get instance name from environment
    instance_name = os.environ.get('LIGHTSAIL_INSTANCE_NAME', 'wordpress-instance')
    
    print("🧪 Testing Command Visibility")
    print("=" * 50)
    print(f"Instance: {instance_name}")
    print("=" * 50)
    
    # Create Lightsail client
    client = create_lightsail_client(instance_name)
    
    # Test commands that should show clear logging
    test_commands = [
        "echo 'Test command 1: Basic echo'",
        "whoami",
        "pwd",
        "ls -la /tmp",
        "date",
        "uname -a"
    ]
    
    print(f"\n🔍 Will send {len(test_commands)} individual commands to host")
    print("Each command should show:")
    print("  - 📡 Sending command to host message")
    print("  - Command boundaries with dashes")
    print("  - Exact command text")
    print("  - SSH command details")
    print("  - Remote host output")
    print("\n" + "=" * 50)
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n🧪 TEST {i}/{len(test_commands)}")
        print(f"About to send: {cmd}")
        print("-" * 30)
        
        success, output = client.run_command(cmd, timeout=30)
        
        if success:
            print(f"✅ Test {i} completed successfully")
        else:
            print(f"❌ Test {i} failed: {output}")
            
        print("-" * 30)
    
    print("\n🎯 Command visibility test completed!")
    print("Check the logs above to see if each command was clearly shown")

if __name__ == "__main__":
    test_individual_commands()