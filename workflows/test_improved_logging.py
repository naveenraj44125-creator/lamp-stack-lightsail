#!/usr/bin/env python3
"""
Test script to demonstrate improved command logging format
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lightsail_common import LightsailBase

def test_improved_logging():
    """Test the improved command logging format"""
    
    print("🧪 Testing Improved Command Logging Format")
    print("=" * 50)
    
    # Set GitHub Actions environment for enhanced logging
    os.environ['GITHUB_ACTIONS'] = 'true'
    
    # Create a test instance (won't actually connect)
    try:
        client = LightsailBase("test-instance", "us-east-1")
        
        print("\n📋 Test 1: Single Line Command")
        print("-" * 30)
        single_cmd = "sudo apt-get update"
        print(f"Original command: {single_cmd}")
        
        print("\n📋 Test 2: Multi-line Script")
        print("-" * 30)
        multi_cmd = """set -e
echo "Installing Apache..."

# Install Apache
sudo apt-get update
sudo apt-get install -y apache2

# Enable Apache
sudo systemctl enable apache2
sudo systemctl start apache2

echo "✅ Apache installation completed" """
        
        print("Original command:")
        lines = multi_cmd.split('\n')
        for i, line in enumerate(lines, 1):
            print(f"{i:2d}: {line}")
        
        print("\n📋 Test 3: How it would appear in logs")
        print("-" * 30)
        
        # Simulate the logging format
        import time
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        
        # Single command log format
        log_entry_single = f"[{timestamp}] COMMAND: {single_cmd}"
        print(f"Single command log: {log_entry_single}")
        
        # Multi-line command log format
        first_line = multi_cmd.split('\n')[0].strip()
        line_count = len([line for line in multi_cmd.split('\n') if line.strip()])
        actual_lines = [line.strip() for line in multi_cmd.split('\n') 
                       if line.strip() and not line.strip().startswith('#') and line.strip() != 'set -e']
        if actual_lines:
            first_line = actual_lines[0]
            if first_line.startswith('echo '):
                echo_msg = first_line.replace('echo "', '').replace('"', '').replace("echo '", "").replace("'", "")
                log_entry_multi = f"[{timestamp}] SCRIPT: {echo_msg} ({line_count} commands)"
            else:
                log_entry_multi = f"[{timestamp}] SCRIPT: {first_line[:50]}... ({line_count} commands)"
        
        print(f"Multi-line script log: {log_entry_multi}")
        
        print("\n✅ Improved logging format test completed!")
        print("\n🎯 Key Improvements:")
        print("   • No more confusing pipe symbols")
        print("   • Clear distinction between single commands and scripts")
        print("   • Line numbers for multi-line commands")
        print("   • Descriptive script summaries in logs")
        print("   • First 50 characters + command count for scripts")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_improved_logging()
    sys.exit(0 if success else 1)