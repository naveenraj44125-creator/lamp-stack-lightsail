"""
Unit tests for the FixApplier module.

Tests the blueprint_id fix functionality and other fix operations.
"""

import os
import tempfile
import yaml
import pytest
from fix_applier import FixApplier, FixReport


class TestFixBlueprintId:
    """Tests for the fix_blueprint_id method."""
    
    def test_fix_blueprint_id_with_underscores(self):
        """Test fixing blueprint_id that contains underscores."""
        # Create a temporary config file with underscore format
        config = {
            'lightsail': {
                'instance_name': 'test-instance',
                'blueprint_id': 'ubuntu_22_04'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.safe_dump(config, f)
            config_file = f.name
        
        try:
            # Apply the fix
            fixer = FixApplier(repo_path='.', instance_name='test-instance')
            result = fixer.fix_blueprint_id(config_file)
            
            # Verify the fix was successful
            assert result is True
            
            # Load the updated config and verify the change
            with open(config_file, 'r') as f:
                updated_config = yaml.safe_load(f)
            
            assert updated_config['lightsail']['blueprint_id'] == 'ubuntu-22-04'
            
        finally:
            # Clean up
            os.unlink(config_file)
    
    def test_fix_blueprint_id_already_correct(self):
        """Test fixing blueprint_id that already uses hyphens."""
        # Create a temporary config file with hyphen format
        config = {
            'lightsail': {
                'instance_name': 'test-instance',
                'blueprint_id': 'ubuntu-22-04'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.safe_dump(config, f)
            config_file = f.name
        
        try:
            # Apply the fix
            fixer = FixApplier(repo_path='.', instance_name='test-instance')
            result = fixer.fix_blueprint_id(config_file)
            
            # Verify the fix was successful (no change needed)
            assert result is True
            
            # Load the updated config and verify no change
            with open(config_file, 'r') as f:
                updated_config = yaml.safe_load(f)
            
            assert updated_config['lightsail']['blueprint_id'] == 'ubuntu-22-04'
            
        finally:
            # Clean up
            os.unlink(config_file)
    
    def test_fix_blueprint_id_multiple_underscores(self):
        """Test fixing blueprint_id with multiple underscores."""
        # Create a temporary config file with multiple underscores
        config = {
            'lightsail': {
                'instance_name': 'test-instance',
                'blueprint_id': 'amazon_linux_2023_1_0'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.safe_dump(config, f)
            config_file = f.name
        
        try:
            # Apply the fix
            fixer = FixApplier(repo_path='.', instance_name='test-instance')
            result = fixer.fix_blueprint_id(config_file)
            
            # Verify the fix was successful
            assert result is True
            
            # Load the updated config and verify the change
            with open(config_file, 'r') as f:
                updated_config = yaml.safe_load(f)
            
            assert updated_config['lightsail']['blueprint_id'] == 'amazon-linux-2023-1-0'
            
        finally:
            # Clean up
            os.unlink(config_file)
    
    def test_fix_blueprint_id_missing_lightsail_section(self):
        """Test fixing blueprint_id when lightsail section is missing."""
        # Create a temporary config file without lightsail section
        config = {
            'application': {
                'name': 'test-app'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.safe_dump(config, f)
            config_file = f.name
        
        try:
            # Apply the fix
            fixer = FixApplier(repo_path='.', instance_name='test-instance')
            result = fixer.fix_blueprint_id(config_file)
            
            # Verify the fix failed gracefully
            assert result is False
            
        finally:
            # Clean up
            os.unlink(config_file)
    
    def test_fix_blueprint_id_missing_blueprint_id_field(self):
        """Test fixing blueprint_id when blueprint_id field is missing."""
        # Create a temporary config file without blueprint_id field
        config = {
            'lightsail': {
                'instance_name': 'test-instance'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.safe_dump(config, f)
            config_file = f.name
        
        try:
            # Apply the fix
            fixer = FixApplier(repo_path='.', instance_name='test-instance')
            result = fixer.fix_blueprint_id(config_file)
            
            # Verify the fix failed gracefully
            assert result is False
            
        finally:
            # Clean up
            os.unlink(config_file)
    
    def test_fix_blueprint_id_invalid_file(self):
        """Test fixing blueprint_id with non-existent file."""
        # Use a non-existent file path
        config_file = '/tmp/nonexistent_config_file_12345.yml'
        
        # Apply the fix
        fixer = FixApplier(repo_path='.', instance_name='test-instance')
        result = fixer.fix_blueprint_id(config_file)
        
        # Verify the fix failed gracefully
        assert result is False
    
    def test_fix_blueprint_id_preserves_other_fields(self):
        """Test that fixing blueprint_id preserves other configuration fields."""
        # Create a temporary config file with multiple fields
        config = {
            'aws': {
                'region': 'us-east-1'
            },
            'lightsail': {
                'instance_name': 'test-instance',
                'blueprint_id': 'ubuntu_22_04',
                'bundle_id': 'small_3_0',
                'static_ip': ''
            },
            'application': {
                'name': 'test-app',
                'type': 'nodejs',
                'port': 3000
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.safe_dump(config, f)
            config_file = f.name
        
        try:
            # Apply the fix
            fixer = FixApplier(repo_path='.', instance_name='test-instance')
            result = fixer.fix_blueprint_id(config_file)
            
            # Verify the fix was successful
            assert result is True
            
            # Load the updated config and verify all fields
            with open(config_file, 'r') as f:
                updated_config = yaml.safe_load(f)
            
            # Check that blueprint_id was fixed
            assert updated_config['lightsail']['blueprint_id'] == 'ubuntu-22-04'
            
            # Check that other fields were preserved
            assert updated_config['aws']['region'] == 'us-east-1'
            assert updated_config['lightsail']['instance_name'] == 'test-instance'
            assert updated_config['lightsail']['bundle_id'] == 'small_3_0'
            assert updated_config['lightsail']['static_ip'] == ''
            assert updated_config['application']['name'] == 'test-app'
            assert updated_config['application']['type'] == 'nodejs'
            assert updated_config['application']['port'] == 3000
            
        finally:
            # Clean up
            os.unlink(config_file)


class TestFixApplierInitialization:
    """Tests for FixApplier initialization."""
    
    def test_initialization_with_defaults(self):
        """Test FixApplier initialization with default region."""
        fixer = FixApplier(repo_path='/path/to/repo', instance_name='test-instance')
        
        assert fixer.repo_path == '/path/to/repo'
        assert fixer.instance_name == 'test-instance'
        assert fixer.region == 'us-east-1'
    
    def test_initialization_with_custom_region(self):
        """Test FixApplier initialization with custom region."""
        fixer = FixApplier(
            repo_path='/path/to/repo',
            instance_name='test-instance',
            region='us-west-2'
        )
        
        assert fixer.repo_path == '/path/to/repo'
        assert fixer.instance_name == 'test-instance'
        assert fixer.region == 'us-west-2'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
