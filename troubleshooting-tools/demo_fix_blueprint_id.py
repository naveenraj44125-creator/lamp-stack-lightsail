#!/usr/bin/env python3
"""
Demonstration of the fix_blueprint_id functionality.

This script demonstrates how the FixApplier can fix blueprint_id format
in deployment configuration files.
"""

import os
import shutil
import yaml
from fix_applier import FixApplier


def demo_fix_blueprint_id():
    """Demonstrate the blueprint_id fix on a test config file."""
    
    print("=" * 70)
    print("Blueprint ID Fix Demonstration")
    print("=" * 70)
    print()
    
    # Create a test config file with underscore format
    test_config = {
        'aws': {
            'region': 'us-east-1'
        },
        'lightsail': {
            'instance_name': 'test-nodejs-app',
            'static_ip': '',
            'bundle_id': 'small_3_0',
            'blueprint_id': 'ubuntu_22_04'  # Incorrect format with underscores
        },
        'application': {
            'name': 'test-app',
            'type': 'nodejs',
            'port': 3000
        }
    }
    
    test_config_file = 'test-deployment-config.yml'
    
    # Save the test config
    print(f"1. Creating test config file: {test_config_file}")
    with open(test_config_file, 'w') as f:
        yaml.safe_dump(test_config, f, default_flow_style=False, sort_keys=False)
    
    # Display the original config
    print("\n2. Original configuration:")
    print("-" * 70)
    with open(test_config_file, 'r') as f:
        original_content = f.read()
        print(original_content)
    
    # Apply the fix
    print("\n3. Applying blueprint_id fix...")
    print("-" * 70)
    fixer = FixApplier(repo_path='.', instance_name='test-nodejs-app')
    result = fixer.fix_blueprint_id(test_config_file)
    
    if result:
        print("\n✓ Fix applied successfully!")
    else:
        print("\n✗ Fix failed!")
        return
    
    # Display the updated config
    print("\n4. Updated configuration:")
    print("-" * 70)
    with open(test_config_file, 'r') as f:
        updated_content = f.read()
        print(updated_content)
    
    # Verify the change
    print("\n5. Verification:")
    print("-" * 70)
    with open(test_config_file, 'r') as f:
        updated_config = yaml.safe_load(f)
    
    original_blueprint_id = test_config['lightsail']['blueprint_id']
    updated_blueprint_id = updated_config['lightsail']['blueprint_id']
    
    print(f"Original blueprint_id: {original_blueprint_id}")
    print(f"Updated blueprint_id:  {updated_blueprint_id}")
    
    if '_' in updated_blueprint_id:
        print("\n✗ ERROR: blueprint_id still contains underscores!")
    else:
        print("\n✓ SUCCESS: blueprint_id now uses hyphens!")
    
    # Clean up
    print("\n6. Cleaning up test file...")
    os.unlink(test_config_file)
    print(f"Removed {test_config_file}")
    
    print("\n" + "=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


if __name__ == '__main__':
    demo_fix_blueprint_id()
