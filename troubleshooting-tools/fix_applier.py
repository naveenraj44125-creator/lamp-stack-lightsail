"""
Fix Applier module for applying automated fixes to deployment configurations.

This module provides functionality to:
- Fix blueprint_id format (underscores to hyphens)
- Fix port configuration inconsistencies
- Add health check endpoints to applications
- Fix firewall rules
- Apply all recommended fixes
"""

import os
import yaml
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FixReport:
    """Represents the results of applying fixes."""
    fixes_applied: List[str] = field(default_factory=list)
    fixes_failed: List[str] = field(default_factory=list)
    config_changes: Dict[str, Any] = field(default_factory=dict)
    success: bool = False


class FixApplier:
    """
    Applies automated fixes based on diagnosis.
    
    This class implements various fix operations to resolve common
    deployment configuration issues.
    """
    
    def __init__(self, repo_path: str, instance_name: str, region: str = "us-east-1"):
        """
        Initialize with repository path and instance details.
        
        Args:
            repo_path: Path to the repository containing deployment config
            instance_name: Name of the Lightsail instance
            region: AWS region (default: us-east-1)
        """
        self.repo_path = repo_path
        self.instance_name = instance_name
        self.region = region
    
    def fix_blueprint_id(self, config_file: str) -> bool:
        """
        Fix blueprint_id format (underscores to hyphens).
        
        Converts underscores to hyphens in the blueprint_id field
        to match AWS Lightsail's expected format.
        
        Args:
            config_file: Path to deployment configuration file
            
        Returns:
            True if fix was applied successfully, False otherwise
        """
        print(f"  Fixing blueprint_id in {config_file}...")
        
        try:
            # Load the configuration file
            config = self._load_config(config_file)
            if config is None:
                print(f"    Failed to load config file")
                return False
            
            # Check if lightsail section exists
            if 'lightsail' not in config:
                print(f"    No 'lightsail' section found in config")
                return False
            
            # Check if blueprint_id exists
            if 'blueprint_id' not in config['lightsail']:
                print(f"    No 'blueprint_id' field found in lightsail section")
                return False
            
            # Get current blueprint_id
            current_blueprint_id = config['lightsail']['blueprint_id']
            
            # Check if it contains underscores
            if '_' not in current_blueprint_id:
                print(f"    blueprint_id '{current_blueprint_id}' already uses correct format")
                return True
            
            # Convert underscores to hyphens
            fixed_blueprint_id = current_blueprint_id.replace('_', '-')
            
            # Update the configuration
            config['lightsail']['blueprint_id'] = fixed_blueprint_id
            
            # Save the updated configuration
            if self._save_config(config_file, config):
                print(f"    Successfully updated blueprint_id: '{current_blueprint_id}' -> '{fixed_blueprint_id}'")
                return True
            else:
                print(f"    Failed to save updated config file")
                return False
                
        except Exception as e:
            print(f"    Error fixing blueprint_id: {e}")
            return False
    
    def fix_port_configuration(self, config_file: str, detected_port: int) -> bool:
        """
        Update port configuration to match application.
        
        Args:
            config_file: Path to deployment configuration file
            detected_port: Port number detected from application code
            
        Returns:
            True if fix was applied successfully, False otherwise
        """
        print(f"  Fixing port configuration in {config_file}...")
        
        # Port configuration fix will be implemented in Task 5
        # For now, return False
        return False
    
    def add_health_endpoint(self, app_file: str) -> bool:
        """
        Add default health check endpoint to application.
        
        Args:
            app_file: Path to application entry point file
            
        Returns:
            True if fix was applied successfully, False otherwise
        """
        print(f"  Adding health endpoint to {app_file}...")
        
        # Health endpoint addition will be implemented in Task 5
        # For now, return False
        return False
    
    def fix_firewall_rules(self, config_file: str, port: int) -> bool:
        """
        Add application port to firewall rules.
        
        Args:
            config_file: Path to deployment configuration file
            port: Port number to add to firewall rules
            
        Returns:
            True if fix was applied successfully, False otherwise
        """
        print(f"  Fixing firewall rules in {config_file}...")
        
        # Firewall rules fix will be implemented in Task 5
        # For now, return False
        return False
    
    def apply_all_fixes(self, diagnosis) -> FixReport:
        """
        Apply all recommended fixes.
        
        Args:
            diagnosis: Diagnosis object with recommended fixes
            
        Returns:
            FixReport object with results of fix application
        """
        print("  Applying recommended fixes...")
        
        report = FixReport()
        
        # Fix application logic will be implemented in Task 5
        # For now, return empty report
        report.success = False
        
        return report
    
    def _load_config(self, config_file: str) -> Optional[Dict[str, Any]]:
        """
        Load YAML configuration file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Configuration dictionary or None if loading fails
        """
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"  Error loading config file: {e}")
            return None
    
    def _save_config(self, config_file: str, config: Dict[str, Any]) -> bool:
        """
        Save YAML configuration file.
        
        Args:
            config_file: Path to configuration file
            config: Configuration dictionary
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            with open(config_file, 'w') as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            print(f"  Error saving config file: {e}")
            return False
