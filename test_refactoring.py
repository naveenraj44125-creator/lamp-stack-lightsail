#!/usr/bin/env python3
"""
Test script to verify the refactored workflow code works correctly
This script tests the common functionality without requiring an actual Lightsail instance
"""

import sys
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add workflows directory to path
sys.path.insert(0, 'workflows')

def test_imports():
    """Test that all refactored modules can be imported successfully"""
    print("🧪 Testing imports...")
    
    try:
        # Test common library import
        from lightsail_common import LightsailBase, LightsailSSHManager, LightsailLAMPManager, create_lightsail_client
        print("   ✅ lightsail_common imports successful")
        
        # Test refactored workflow imports
        import importlib.util
        
        # Import modules with hyphens in names
        spec = importlib.util.spec_from_file_location("deploy_pre_steps", "workflows/deploy-pre-steps.py")
        deploy_pre_steps = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deploy_pre_steps)
        print("   ✅ deploy-pre-steps imports successful")
        
        spec = importlib.util.spec_from_file_location("deploy_post_steps", "workflows/deploy-post-steps.py")
        deploy_post_steps = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deploy_post_steps)
        print("   ✅ deploy-post-steps imports successful")
        
        spec = importlib.util.spec_from_file_location("verify_deployment", "workflows/verify-deployment.py")
        verify_deployment = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verify_deployment)
        print("   ✅ verify-deployment imports successful")
        
        spec = importlib.util.spec_from_file_location("install_lamp_on_lightsail_enhanced", "workflows/install-lamp-on-lightsail-enhanced.py")
        install_lamp_on_lightsail_enhanced = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(install_lamp_on_lightsail_enhanced)
        print("   ✅ install-lamp-on-lightsail-enhanced imports successful")
        
        spec = importlib.util.spec_from_file_location("deploy_with_run_command", "workflows/deploy-with-run-command.py")
        deploy_with_run_command = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deploy_with_run_command)
        print("   ✅ deploy-with-run-command imports successful")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_factory_function():
    """Test the factory function creates correct client types"""
    print("🧪 Testing factory function...")
    
    try:
        from lightsail_common import create_lightsail_client, LightsailBase, LightsailSSHManager, LightsailLAMPManager
        
        # Mock boto3 to avoid AWS credentials requirement
        with patch('lightsail_common.boto3') as mock_boto3:
            mock_client = Mock()
            mock_boto3.client.return_value = mock_client
            
            # Test base client creation
            base_client = create_lightsail_client('test-instance', 'us-east-1', 'base')
            assert isinstance(base_client, LightsailBase)
            print("   ✅ Base client creation successful")
            
            # Test SSH client creation
            ssh_client = create_lightsail_client('test-instance', 'us-east-1', 'ssh')
            assert isinstance(ssh_client, LightsailSSHManager)
            print("   ✅ SSH client creation successful")
            
            # Test LAMP client creation
            lamp_client = create_lightsail_client('test-instance', 'us-east-1', 'lamp')
            assert isinstance(lamp_client, LightsailLAMPManager)
            print("   ✅ LAMP client creation successful")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Factory function test failed: {e}")
        return False

def test_lamp_scripts():
    """Test that LAMP manager provides expected scripts"""
    print("🧪 Testing LAMP scripts...")
    
    try:
        from lightsail_common import LightsailLAMPManager
        
        # Mock boto3 to avoid AWS credentials requirement
        with patch('lightsail_common.boto3') as mock_boto3:
            mock_client = Mock()
            mock_boto3.client.return_value = mock_client
            
            lamp_manager = LightsailLAMPManager('test-instance', 'us-east-1')
            
            # Test script methods exist and return strings
            install_script = lamp_manager.get_lamp_install_script()
            assert isinstance(install_script, str) and len(install_script) > 100
            print("   ✅ LAMP install script available")
            
            db_script = lamp_manager.get_database_setup_script()
            assert isinstance(db_script, str) and 'mysql' in db_script.lower()
            print("   ✅ Database setup script available")
            
            deploy_script = lamp_manager.get_deployment_script()
            assert isinstance(deploy_script, str) and 'tar' in deploy_script
            print("   ✅ Deployment script available")
            
            verify_script = lamp_manager.get_verification_script()
            assert isinstance(verify_script, str) and 'apache2' in verify_script.lower()
            print("   ✅ Verification script available")
            
        return True
        
    except Exception as e:
        print(f"   ❌ LAMP scripts test failed: {e}")
        return False

def test_ssh_functionality():
    """Test SSH functionality without creating actual key files"""
    print("🧪 Testing SSH functionality...")
    
    try:
        from lightsail_common import LightsailBase
        
        # Mock boto3 to avoid AWS credentials requirement
        with patch('lightsail_common.boto3') as mock_boto3:
            mock_client = Mock()
            mock_boto3.client.return_value = mock_client
            
            base_client = LightsailBase('test-instance', 'us-east-1')
            
            # Test that SSH methods exist
            assert hasattr(base_client, 'create_ssh_files')
            assert hasattr(base_client, 'run_command')
            assert hasattr(base_client, 'upload_file')
            print("   ✅ SSH methods available")
            
            # Test connection error detection
            assert base_client._is_connection_error("Connection refused")
            assert not base_client._is_connection_error("Permission denied")
            print("   ✅ Connection error detection working")
            
        return True
        
    except Exception as e:
        print(f"   ❌ SSH functionality test failed: {e}")
        return False

def test_workflow_classes():
    """Test that workflow classes can be instantiated"""
    print("🧪 Testing workflow class instantiation...")
    
    try:
        # Mock boto3 for all imports
        with patch('lightsail_common.boto3') as mock_boto3:
            mock_client = Mock()
            mock_boto3.client.return_value = mock_client
            
            # Import modules with hyphens in names
            import importlib.util
            
            # Test pre-deployer
            spec = importlib.util.spec_from_file_location("deploy_pre_steps", "workflows/deploy-pre-steps.py")
            deploy_pre_steps = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(deploy_pre_steps)
            pre_deployer = deploy_pre_steps.LightsailPreDeployer('test-instance', 'us-east-1')
            assert hasattr(pre_deployer, 'client')
            print("   ✅ LightsailPreDeployer instantiation successful")
            
            # Test post-deployer
            spec = importlib.util.spec_from_file_location("deploy_post_steps", "workflows/deploy-post-steps.py")
            deploy_post_steps = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(deploy_post_steps)
            post_deployer = deploy_post_steps.LightsailPostDeployer('test-instance', 'us-east-1')
            assert hasattr(post_deployer, 'client')
            print("   ✅ LightsailPostDeployer instantiation successful")
            
            # Test verifier
            spec = importlib.util.spec_from_file_location("verify_deployment", "workflows/verify-deployment.py")
            verify_deployment = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(verify_deployment)
            verifier = verify_deployment.LightsailVerifier('test-instance', 'us-east-1')
            assert hasattr(verifier, 'client')
            print("   ✅ LightsailVerifier instantiation successful")
            
            # Test installer
            spec = importlib.util.spec_from_file_location("install_lamp_on_lightsail_enhanced", "workflows/install-lamp-on-lightsail-enhanced.py")
            install_lamp_on_lightsail_enhanced = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(install_lamp_on_lightsail_enhanced)
            installer = install_lamp_on_lightsail_enhanced.LightsailLAMPInstaller('test-instance', 'us-east-1')
            assert hasattr(installer, 'client')
            print("   ✅ LightsailLAMPInstaller instantiation successful")
            
            # Test deployer
            spec = importlib.util.spec_from_file_location("deploy_with_run_command", "workflows/deploy-with-run-command.py")
            deploy_with_run_command = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(deploy_with_run_command)
            deployer = deploy_with_run_command.LightsailDeployer('test-instance', 'us-east-1')
            assert hasattr(deployer, 'client')
            print("   ✅ LightsailDeployer instantiation successful")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Workflow class instantiation test failed: {e}")
        return False

def test_error_detection():
    """Test connection error detection functionality"""
    print("🧪 Testing error detection...")
    
    try:
        from lightsail_common import LightsailBase
        
        # Mock boto3 to avoid AWS credentials requirement
        with patch('lightsail_common.boto3') as mock_boto3:
            mock_client = Mock()
            mock_boto3.client.return_value = mock_client
            
            base_client = LightsailBase('test-instance', 'us-east-1')
            
            # Test connection error detection
            connection_errors = [
                "Connection refused",
                "Broken pipe",
                "Connection timed out",
                "Network unreachable",
                "ssh_exchange_identification: Connection closed by remote host"
            ]
            
            for error in connection_errors:
                assert base_client._is_connection_error(error)
                print(f"   ✅ Detected connection error: {error[:30]}...")
            
            # Test non-connection errors
            non_connection_errors = [
                "Permission denied",
                "Command not found",
                "Syntax error"
            ]
            
            for error in non_connection_errors:
                assert not base_client._is_connection_error(error)
                print(f"   ✅ Correctly ignored non-connection error: {error}")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error detection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting refactoring verification tests...\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Factory Function Tests", test_factory_function),
        ("LAMP Scripts Tests", test_lamp_scripts),
        ("SSH Functionality Tests", test_ssh_functionality),
        ("Workflow Classes Tests", test_workflow_classes),
        ("Error Detection Tests", test_error_detection)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 50)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Refactoring verification successful.")
        return 0
    else:
        print("💥 Some tests failed. Please check the refactoring.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
