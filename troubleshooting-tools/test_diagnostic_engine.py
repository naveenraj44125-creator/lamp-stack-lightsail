"""
Unit tests for DiagnosticEngine module.

Tests instance state checking, SSH connectivity, application diagnostics,
and failure diagnosis functionality.
"""

import unittest
import subprocess
from unittest.mock import Mock, patch, MagicMock
from diagnostic_engine import (
    DiagnosticEngine,
    InstanceState,
    SSHStatus,
    AppDiagnostics,
    EndpointResult,
    EndpointResults,
    Diagnosis
)


class TestDiagnosticEngine(unittest.TestCase):
    """Test cases for DiagnosticEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.instance_name = "test-instance"
        self.region = "us-east-1"
    
    @patch('diagnostic_engine.boto3.client')
    def test_check_instance_state_success(self, mock_boto_client):
        """Test successful instance state check."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance.return_value = {
            'instance': {
                'name': self.instance_name,
                'state': {'name': 'running'},
                'publicIpAddress': '54.123.45.67',
                'blueprintId': 'ubuntu-22-04'
            }
        }
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.check_instance_state()
        
        # Assert
        self.assertTrue(result.exists)
        self.assertEqual(result.state, 'running')
        self.assertEqual(result.public_ip, '54.123.45.67')
        self.assertEqual(result.blueprint_id, 'ubuntu-22-04')
        mock_lightsail.get_instance.assert_called_once_with(
            instanceName=self.instance_name
        )
    
    @patch('diagnostic_engine.boto3.client')
    def test_check_instance_state_not_found(self, mock_boto_client):
        """Test instance state check when instance doesn't exist."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Simulate NotFoundException
        mock_lightsail.exceptions.NotFoundException = type('NotFoundException', (Exception,), {})
        mock_lightsail.get_instance.side_effect = mock_lightsail.exceptions.NotFoundException()
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.check_instance_state()
        
        # Assert
        self.assertFalse(result.exists)
        self.assertEqual(result.state, 'not_found')
        self.assertEqual(result.public_ip, '')
        self.assertEqual(result.blueprint_id, '')
    
    @patch('diagnostic_engine.boto3.client')
    def test_check_instance_state_stopped(self, mock_boto_client):
        """Test instance state check when instance is stopped."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance.return_value = {
            'instance': {
                'name': self.instance_name,
                'state': {'name': 'stopped'},
                'publicIpAddress': '54.123.45.67',
                'blueprintId': 'ubuntu-22-04'
            }
        }
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.check_instance_state()
        
        # Assert
        self.assertTrue(result.exists)
        self.assertEqual(result.state, 'stopped')
        self.assertEqual(result.public_ip, '54.123.45.67')
    
    @patch('diagnostic_engine.boto3.client')
    def test_check_instance_state_pending(self, mock_boto_client):
        """Test instance state check when instance is pending."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance.return_value = {
            'instance': {
                'name': self.instance_name,
                'state': {'name': 'pending'},
                'publicIpAddress': '',
                'blueprintId': 'ubuntu-22-04'
            }
        }
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.check_instance_state()
        
        # Assert
        self.assertTrue(result.exists)
        self.assertEqual(result.state, 'pending')
        self.assertEqual(result.public_ip, '')
    
    @patch('diagnostic_engine.boto3.client')
    def test_check_instance_state_missing_optional_fields(self, mock_boto_client):
        """Test instance state check when optional fields are missing."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance.return_value = {
            'instance': {
                'name': self.instance_name,
                'state': {'name': 'running'}
                # Missing publicIpAddress and blueprintId
            }
        }
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.check_instance_state()
        
        # Assert
        self.assertTrue(result.exists)
        self.assertEqual(result.state, 'running')
        self.assertEqual(result.public_ip, '')
        self.assertEqual(result.blueprint_id, '')
    
    @patch('diagnostic_engine.boto3.client')
    def test_check_instance_state_generic_error(self, mock_boto_client):
        """Test instance state check with generic error."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance.side_effect = Exception("Network error")
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.check_instance_state()
        
        # Assert
        self.assertFalse(result.exists)
        self.assertEqual(result.state, 'error')
    
    @patch('diagnostic_engine.boto3.client')
    def test_initialization(self, mock_boto_client):
        """Test DiagnosticEngine initialization."""
        # Arrange & Act
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Assert
        self.assertEqual(engine.instance_name, self.instance_name)
        self.assertEqual(engine.region, self.region)
        mock_boto_client.assert_called_once_with('lightsail', region_name=self.region)


class TestInstanceState(unittest.TestCase):
    """Test cases for InstanceState data class."""
    
    def test_instance_state_creation(self):
        """Test creating InstanceState with all fields."""
        state = InstanceState(
            exists=True,
            state='running',
            public_ip='54.123.45.67',
            blueprint_id='ubuntu-22-04'
        )
        
        self.assertTrue(state.exists)
        self.assertEqual(state.state, 'running')
        self.assertEqual(state.public_ip, '54.123.45.67')
        self.assertEqual(state.blueprint_id, 'ubuntu-22-04')
    
    def test_instance_state_defaults(self):
        """Test InstanceState with default values."""
        state = InstanceState(exists=False, state='not_found')
        
        self.assertFalse(state.exists)
        self.assertEqual(state.state, 'not_found')
        self.assertEqual(state.public_ip, '')
        self.assertEqual(state.blueprint_id, '')


class TestSSHConnectivity(unittest.TestCase):
    """Test cases for SSH connectivity testing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.instance_name = "test-instance"
        self.region = "us-east-1"
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_ssh_connectivity_success(self, mock_subprocess, mock_boto_client):
        """Test successful SSH connection on first attempt."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance_access_details.return_value = {
            'accessDetails': {
                'ipAddress': '54.123.45.67',
                'username': 'ubuntu',
                'privateKey': 'fake-private-key',
                'certKey': 'ssh-rsa AAAAB3... fake-cert'
            }
        }
        
        # Mock successful SSH command
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "SSH test successful"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_ssh_connectivity(max_retries=3)
        
        # Assert
        self.assertTrue(result.accessible)
        self.assertEqual(result.error_message, "")
        self.assertGreater(result.connection_time, 0)
        mock_lightsail.get_instance_access_details.assert_called_once()
        mock_subprocess.assert_called_once()
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    @patch('diagnostic_engine.time.sleep')
    def test_ssh_connectivity_retry_success(self, mock_sleep, mock_subprocess, mock_boto_client):
        """Test SSH connection succeeds after retry."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance_access_details.return_value = {
            'accessDetails': {
                'ipAddress': '54.123.45.67',
                'username': 'ubuntu',
                'privateKey': 'fake-private-key',
                'certKey': 'ssh-rsa AAAAB3... fake-cert'
            }
        }
        
        # Mock first attempt fails, second succeeds
        mock_result_fail = Mock()
        mock_result_fail.returncode = 255
        mock_result_fail.stderr = "Connection refused"
        
        mock_result_success = Mock()
        mock_result_success.returncode = 0
        mock_result_success.stdout = "SSH test successful"
        mock_result_success.stderr = ""
        
        mock_subprocess.side_effect = [mock_result_fail, mock_result_success]
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_ssh_connectivity(max_retries=3)
        
        # Assert
        self.assertTrue(result.accessible)
        self.assertEqual(result.error_message, "")
        self.assertEqual(mock_subprocess.call_count, 2)
        mock_sleep.assert_called_once_with(10)  # First retry waits 10s
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    @patch('diagnostic_engine.time.sleep')
    def test_ssh_connectivity_exponential_backoff(self, mock_sleep, mock_subprocess, mock_boto_client):
        """Test exponential backoff timing for retries."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance_access_details.return_value = {
            'accessDetails': {
                'ipAddress': '54.123.45.67',
                'username': 'ubuntu',
                'privateKey': 'fake-private-key',
                'certKey': 'ssh-rsa AAAAB3... fake-cert'
            }
        }
        
        # Mock all attempts fail
        mock_result = Mock()
        mock_result.returncode = 255
        mock_result.stderr = "Connection refused"
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_ssh_connectivity(max_retries=3)
        
        # Assert
        self.assertFalse(result.accessible)
        self.assertEqual(mock_subprocess.call_count, 3)
        # Verify exponential backoff: 10s, 20s
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_any_call(10)  # First retry
        mock_sleep.assert_any_call(20)  # Second retry
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_ssh_connectivity_timeout(self, mock_subprocess, mock_boto_client):
        """Test SSH connection timeout handling."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance_access_details.return_value = {
            'accessDetails': {
                'ipAddress': '54.123.45.67',
                'username': 'ubuntu',
                'privateKey': 'fake-private-key',
                'certKey': 'ssh-rsa AAAAB3... fake-cert'
            }
        }
        
        # Mock timeout
        mock_subprocess.side_effect = subprocess.TimeoutExpired('ssh', 30)
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_ssh_connectivity(max_retries=1)
        
        # Assert
        self.assertFalse(result.accessible)
        self.assertIn("timeout", result.error_message.lower())
        self.assertEqual(result.connection_time, 30.0)
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_ssh_connectivity_max_retries_exceeded(self, mock_subprocess, mock_boto_client):
        """Test SSH connection fails after max retries."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance_access_details.return_value = {
            'accessDetails': {
                'ipAddress': '54.123.45.67',
                'username': 'ubuntu',
                'privateKey': 'fake-private-key',
                'certKey': 'ssh-rsa AAAAB3... fake-cert'
            }
        }
        
        # Mock all attempts fail
        mock_result = Mock()
        mock_result.returncode = 255
        mock_result.stderr = "Connection refused"
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_ssh_connectivity(max_retries=3)
        
        # Assert
        self.assertFalse(result.accessible)
        self.assertIn("Connection refused", result.error_message)
        self.assertEqual(mock_subprocess.call_count, 3)
    
    @patch('diagnostic_engine.boto3.client')
    def test_ssh_connectivity_instance_not_found(self, mock_boto_client):
        """Test SSH connection when instance access details cannot be retrieved."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Simulate NotFoundException
        mock_lightsail.exceptions.NotFoundException = type('NotFoundException', (Exception,), {})
        mock_lightsail.get_instance_access_details.side_effect = mock_lightsail.exceptions.NotFoundException()
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_ssh_connectivity(max_retries=1)
        
        # Assert
        self.assertFalse(result.accessible)
        # Error message should be present (empty string means exception was caught)
        self.assertIsNotNone(result.error_message)
    
    def test_is_connection_error(self):
        """Test connection error detection."""
        # Arrange
        engine = DiagnosticEngine("test-instance", "us-east-1")
        
        # Act & Assert
        self.assertTrue(engine._is_connection_error("Connection refused"))
        self.assertTrue(engine._is_connection_error("Connection timed out"))
        self.assertTrue(engine._is_connection_error("Network unreachable"))
        self.assertTrue(engine._is_connection_error("Broken pipe"))
        self.assertFalse(engine._is_connection_error("Permission denied"))
        self.assertFalse(engine._is_connection_error("Invalid key"))


class TestSSHStatus(unittest.TestCase):
    """Test cases for SSHStatus data class."""
    
    def test_ssh_status_success(self):
        """Test creating SSHStatus for successful connection."""
        status = SSHStatus(
            accessible=True,
            error_message="",
            connection_time=1.5
        )
        
        self.assertTrue(status.accessible)
        self.assertEqual(status.error_message, "")
        self.assertEqual(status.connection_time, 1.5)
    
    def test_ssh_status_failure(self):
        """Test creating SSHStatus for failed connection."""
        status = SSHStatus(
            accessible=False,
            error_message="Connection refused",
            connection_time=0.0
        )
        
        self.assertFalse(status.accessible)
        self.assertEqual(status.error_message, "Connection refused")
        self.assertEqual(status.connection_time, 0.0)
    
    def test_ssh_status_defaults(self):
        """Test SSHStatus with default values."""
        status = SSHStatus(accessible=False)
        
        self.assertFalse(status.accessible)
        self.assertEqual(status.error_message, "")
        self.assertEqual(status.connection_time, 0.0)


class TestApplicationDiagnostics(unittest.TestCase):
    """Test cases for application diagnostics."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.instance_name = "test-instance"
        self.region = "us-east-1"
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_run_application_diagnostics_success(self, mock_subprocess, mock_boto_client):
        """Test successful application diagnostics."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance_access_details.return_value = {
            'accessDetails': {
                'ipAddress': '54.123.45.67',
                'username': 'ubuntu',
                'privateKey': 'fake-private-key',
                'certKey': 'ssh-rsa AAAAB3... fake-cert'
            }
        }
        
        # Mock SSH command responses
        mock_results = [
            Mock(returncode=0, stdout='v18.16.0\n', stderr=''),  # Node.js version
            Mock(returncode=0, stdout='installed\n', stderr=''),  # npm check
            Mock(returncode=0, stdout='┌─────┬────────┬─────────┬─────────┐\n│ id  │ name   │ mode    │ status  │\n├─────┼────────┼─────────┼─────────┤\n│ 0   │ app    │ fork    │ online  │\n└─────┴────────┴─────────┴─────────┘\n', stderr=''),  # PM2 status
            Mock(returncode=0, stdout='[2024-01-01 12:00:00] App started\n[2024-01-01 12:00:01] Server listening on port 3000\n', stderr=''),  # App logs
            Mock(returncode=0, stdout='200\n', stderr='')  # Localhost test
        ]
        mock_subprocess.side_effect = mock_results
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.run_application_diagnostics()
        
        # Assert
        self.assertEqual(result.nodejs_version, 'v18.16.0')
        self.assertTrue(result.npm_installed)
        self.assertIn('online', result.pm2_status)
        self.assertIn('App started', result.app_logs)
        self.assertTrue(result.localhost_accessible)
        self.assertEqual(mock_subprocess.call_count, 5)
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_run_application_diagnostics_nodejs_not_installed(self, mock_subprocess, mock_boto_client):
        """Test diagnostics when Node.js is not installed."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance_access_details.return_value = {
            'accessDetails': {
                'ipAddress': '54.123.45.67',
                'username': 'ubuntu',
                'privateKey': 'fake-private-key',
                'certKey': 'ssh-rsa AAAAB3... fake-cert'
            }
        }
        
        # Mock SSH command responses
        mock_results = [
            Mock(returncode=0, stdout='not_installed\n', stderr=''),  # Node.js not installed
            Mock(returncode=0, stdout='not_installed\n', stderr=''),  # npm not installed
            Mock(returncode=0, stdout='pm2_not_available\n', stderr=''),  # PM2 not available
            Mock(returncode=0, stdout='logs_not_available\n', stderr=''),  # Logs not available
            Mock(returncode=0, stdout='failed\n', stderr='')  # Localhost test failed
        ]
        mock_subprocess.side_effect = mock_results
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.run_application_diagnostics()
        
        # Assert
        self.assertEqual(result.nodejs_version, 'not_installed')
        self.assertFalse(result.npm_installed)
        self.assertEqual(result.pm2_status, 'pm2_not_available')
        self.assertEqual(result.app_logs, 'logs_not_available')
        self.assertFalse(result.localhost_accessible)
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_run_application_diagnostics_localhost_accessible_with_redirect(self, mock_subprocess, mock_boto_client):
        """Test localhost accessibility with HTTP redirect (3xx)."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance_access_details.return_value = {
            'accessDetails': {
                'ipAddress': '54.123.45.67',
                'username': 'ubuntu',
                'privateKey': 'fake-private-key',
                'certKey': 'ssh-rsa AAAAB3... fake-cert'
            }
        }
        
        # Mock SSH command responses
        mock_results = [
            Mock(returncode=0, stdout='v18.16.0\n', stderr=''),
            Mock(returncode=0, stdout='installed\n', stderr=''),
            Mock(returncode=0, stdout='app online\n', stderr=''),
            Mock(returncode=0, stdout='logs\n', stderr=''),
            Mock(returncode=0, stdout='301\n', stderr='')  # HTTP redirect
        ]
        mock_subprocess.side_effect = mock_results
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.run_application_diagnostics()
        
        # Assert
        self.assertTrue(result.localhost_accessible)  # 301 is in 200-399 range
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_run_application_diagnostics_localhost_not_accessible(self, mock_subprocess, mock_boto_client):
        """Test localhost not accessible (4xx/5xx errors)."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_lightsail.get_instance_access_details.return_value = {
            'accessDetails': {
                'ipAddress': '54.123.45.67',
                'username': 'ubuntu',
                'privateKey': 'fake-private-key',
                'certKey': 'ssh-rsa AAAAB3... fake-cert'
            }
        }
        
        # Mock SSH command responses
        mock_results = [
            Mock(returncode=0, stdout='v18.16.0\n', stderr=''),
            Mock(returncode=0, stdout='installed\n', stderr=''),
            Mock(returncode=0, stdout='app online\n', stderr=''),
            Mock(returncode=0, stdout='logs\n', stderr=''),
            Mock(returncode=0, stdout='500\n', stderr='')  # HTTP 500 error
        ]
        mock_subprocess.side_effect = mock_results
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.run_application_diagnostics()
        
        # Assert
        self.assertFalse(result.localhost_accessible)  # 500 is >= 400
    
    @patch('diagnostic_engine.boto3.client')
    def test_run_application_diagnostics_ssh_error(self, mock_boto_client):
        """Test diagnostics when SSH access fails."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Simulate SSH access error
        mock_lightsail.get_instance_access_details.side_effect = Exception("SSH access denied")
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.run_application_diagnostics()
        
        # Assert
        self.assertIn('error', result.nodejs_version.lower())
        self.assertFalse(result.npm_installed)
        self.assertEqual(result.pm2_status, '')
        self.assertEqual(result.app_logs, '')
        self.assertFalse(result.localhost_accessible)
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_run_ssh_command_success(self, mock_subprocess, mock_boto_client):
        """Test _run_ssh_command helper method."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        ssh_details = {
            'ipAddress': '54.123.45.67',
            'username': 'ubuntu'
        }
        
        mock_result = Mock(returncode=0, stdout='command output\n', stderr='')
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine._run_ssh_command(ssh_details, '/tmp/key', '/tmp/cert', 'echo test')
        
        # Assert
        self.assertEqual(result, 'command output\n')
        mock_subprocess.assert_called_once()
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_run_ssh_command_failure(self, mock_subprocess, mock_boto_client):
        """Test _run_ssh_command with command failure."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        ssh_details = {
            'ipAddress': '54.123.45.67',
            'username': 'ubuntu'
        }
        
        mock_result = Mock(returncode=1, stdout='', stderr='command failed\n')
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine._run_ssh_command(ssh_details, '/tmp/key', '/tmp/cert', 'false')
        
        # Assert
        self.assertEqual(result, 'command failed\n')


class TestAppDiagnostics(unittest.TestCase):
    """Test cases for AppDiagnostics data class."""
    
    def test_app_diagnostics_creation(self):
        """Test creating AppDiagnostics with all fields."""
        diagnostics = AppDiagnostics(
            nodejs_version='v18.16.0',
            npm_installed=True,
            pm2_status='app online',
            app_logs='Server started',
            localhost_accessible=True
        )
        
        self.assertEqual(diagnostics.nodejs_version, 'v18.16.0')
        self.assertTrue(diagnostics.npm_installed)
        self.assertEqual(diagnostics.pm2_status, 'app online')
        self.assertEqual(diagnostics.app_logs, 'Server started')
        self.assertTrue(diagnostics.localhost_accessible)
    
    def test_app_diagnostics_defaults(self):
        """Test AppDiagnostics with default values."""
        diagnostics = AppDiagnostics()
        
        self.assertEqual(diagnostics.nodejs_version, '')
        self.assertFalse(diagnostics.npm_installed)
        self.assertEqual(diagnostics.pm2_status, '')
        self.assertEqual(diagnostics.app_logs, '')
        self.assertFalse(diagnostics.localhost_accessible)


class TestHealthEndpointTesting(unittest.TestCase):
    """Test cases for health endpoint testing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.instance_name = "test-instance"
        self.region = "us-east-1"
        self.public_ip = "54.123.45.67"
        self.port = 3000
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_health_endpoint_success(self, mock_subprocess, mock_boto_client):
        """Test successful health endpoint check on first attempt."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Mock successful curl response with HTTP 200
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"status":"healthy"}200'  # Body + status code
        mock_result.stderr = ''
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_health_endpoints(
            self.public_ip, 
            ['/api/health'], 
            self.port, 
            max_retries=3
        )
        
        # Assert
        self.assertTrue(result.any_successful)
        self.assertEqual(len(result.results), 1)
        self.assertTrue(result.results[0].accessible)
        self.assertEqual(result.results[0].status_code, 200)
        self.assertEqual(result.results[0].endpoint, '/api/health')
        self.assertIn('healthy', result.results[0].response_body)
        mock_subprocess.assert_called_once()
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_health_endpoint_multiple_endpoints(self, mock_subprocess, mock_boto_client):
        """Test multiple health endpoints."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Mock responses for different endpoints
        mock_results = [
            Mock(returncode=0, stdout='{"status":"ok"}200', stderr=''),  # /
            Mock(returncode=0, stdout='{"health":"good"}200', stderr=''),  # /api/health
            Mock(returncode=0, stdout='{"version":"1.0"}200', stderr=''),  # /api/info
        ]
        mock_subprocess.side_effect = mock_results
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_health_endpoints(
            self.public_ip,
            ['/', '/api/health', '/api/info'],
            self.port,
            max_retries=1
        )
        
        # Assert
        self.assertTrue(result.any_successful)
        self.assertEqual(len(result.results), 3)
        self.assertTrue(all(r.accessible for r in result.results))
        self.assertTrue(all(r.status_code == 200 for r in result.results))
        self.assertEqual(mock_subprocess.call_count, 3)
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    @patch('diagnostic_engine.time.sleep')
    def test_health_endpoint_retry_success(self, mock_sleep, mock_subprocess, mock_boto_client):
        """Test health endpoint succeeds after retry."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Mock first attempt fails, second succeeds
        mock_results = [
            Mock(returncode=0, stdout='503', stderr=''),  # Service unavailable
            Mock(returncode=0, stdout='{"status":"ok"}200', stderr='')  # Success
        ]
        mock_subprocess.side_effect = mock_results
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_health_endpoints(
            self.public_ip,
            ['/api/health'],
            self.port,
            max_retries=3
        )
        
        # Assert
        self.assertTrue(result.any_successful)
        self.assertEqual(len(result.results), 1)
        self.assertTrue(result.results[0].accessible)
        self.assertEqual(result.results[0].status_code, 200)
        self.assertEqual(mock_subprocess.call_count, 2)
        mock_sleep.assert_called_once_with(15)  # 15 second retry interval
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    @patch('diagnostic_engine.time.sleep')
    def test_health_endpoint_max_retries(self, mock_sleep, mock_subprocess, mock_boto_client):
        """Test health endpoint fails after max retries."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Mock all attempts fail with 503
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '503'
        mock_result.stderr = ''
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_health_endpoints(
            self.public_ip,
            ['/api/health'],
            self.port,
            max_retries=3
        )
        
        # Assert
        self.assertFalse(result.any_successful)
        self.assertEqual(len(result.results), 1)
        self.assertTrue(result.results[0].accessible)  # Endpoint is accessible but returns 503
        self.assertEqual(result.results[0].status_code, 503)
        self.assertEqual(mock_subprocess.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # Retries 2 and 3
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_health_endpoint_http_404(self, mock_subprocess, mock_boto_client):
        """Test health endpoint returns 404 (not retriable)."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Mock 404 response
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'Not Found404'
        mock_result.stderr = ''
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_health_endpoints(
            self.public_ip,
            ['/api/health'],
            self.port,
            max_retries=3
        )
        
        # Assert
        self.assertFalse(result.any_successful)
        self.assertEqual(len(result.results), 1)
        self.assertTrue(result.results[0].accessible)
        self.assertEqual(result.results[0].status_code, 404)
        self.assertEqual(result.results[0].response_body, 'Not Found')
        mock_subprocess.assert_called_once()  # No retry for 404
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_health_endpoint_timeout(self, mock_subprocess, mock_boto_client):
        """Test health endpoint timeout."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Mock timeout
        mock_subprocess.side_effect = subprocess.TimeoutExpired('curl', 15)
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_health_endpoints(
            self.public_ip,
            ['/api/health'],
            self.port,
            max_retries=1
        )
        
        # Assert
        self.assertFalse(result.any_successful)
        self.assertEqual(len(result.results), 1)
        self.assertFalse(result.results[0].accessible)
        self.assertIsNone(result.results[0].status_code)
        self.assertIn('timeout', result.results[0].error_message.lower())
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_health_endpoint_connection_refused(self, mock_subprocess, mock_boto_client):
        """Test health endpoint connection refused."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Mock connection refused error
        mock_subprocess.side_effect = Exception("Connection refused")
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_health_endpoints(
            self.public_ip,
            ['/api/health'],
            self.port,
            max_retries=1
        )
        
        # Assert
        self.assertFalse(result.any_successful)
        self.assertEqual(len(result.results), 1)
        self.assertFalse(result.results[0].accessible)
        self.assertIsNone(result.results[0].status_code)
        self.assertIn('Connection refused', result.results[0].error_message)
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_health_endpoint_invalid_response(self, mock_subprocess, mock_boto_client):
        """Test health endpoint with invalid response."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Mock invalid response (too short)
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'ab'  # Less than 3 characters
        mock_result.stderr = ''
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_health_endpoints(
            self.public_ip,
            ['/api/health'],
            self.port,
            max_retries=1
        )
        
        # Assert
        self.assertFalse(result.any_successful)
        self.assertEqual(len(result.results), 1)
        self.assertFalse(result.results[0].accessible)
        self.assertIsNone(result.results[0].status_code)
        self.assertIn('invalid', result.results[0].error_message.lower())
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_health_endpoint_non_numeric_status(self, mock_subprocess, mock_boto_client):
        """Test health endpoint with non-numeric status code."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        # Mock response with non-numeric status
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = 'response bodyXYZ'  # Last 3 chars not numeric
        mock_result.stderr = ''
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act
        result = engine.test_health_endpoints(
            self.public_ip,
            ['/api/health'],
            self.port,
            max_retries=1
        )
        
        # Assert
        self.assertFalse(result.any_successful)
        self.assertEqual(len(result.results), 1)
        self.assertFalse(result.results[0].accessible)
        self.assertIsNone(result.results[0].status_code)
    
    @patch('diagnostic_engine.boto3.client')
    def test_is_retriable_http_status(self, mock_boto_client):
        """Test retriable HTTP status code detection."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Act & Assert
        # Retriable status codes
        self.assertTrue(engine._is_retriable_http_status(500))
        self.assertTrue(engine._is_retriable_http_status(502))
        self.assertTrue(engine._is_retriable_http_status(503))
        self.assertTrue(engine._is_retriable_http_status(504))
        
        # Non-retriable status codes
        self.assertFalse(engine._is_retriable_http_status(200))
        self.assertFalse(engine._is_retriable_http_status(404))
        self.assertFalse(engine._is_retriable_http_status(400))
        self.assertFalse(engine._is_retriable_http_status(401))
        self.assertFalse(engine._is_retriable_http_status(403))
    
    @patch('diagnostic_engine.boto3.client')
    @patch('diagnostic_engine.subprocess.run')
    def test_health_endpoint_configurable_port(self, mock_subprocess, mock_boto_client):
        """Test health endpoint with custom port."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"status":"ok"}200'
        mock_result.stderr = ''
        mock_subprocess.return_value = mock_result
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        custom_port = 8080
        
        # Act
        result = engine.test_health_endpoints(
            self.public_ip,
            ['/health'],
            custom_port,
            max_retries=1
        )
        
        # Assert
        self.assertTrue(result.any_successful)
        # Verify curl was called with correct port
        call_args = mock_subprocess.call_args[0][0]
        self.assertIn(f'http://{self.public_ip}:{custom_port}/health', call_args)


class TestEndpointDataClasses(unittest.TestCase):
    """Test cases for endpoint-related data classes."""
    
    def test_endpoint_result_creation(self):
        """Test creating EndpointResult with all fields."""
        result = EndpointResult(
            endpoint='/api/health',
            status_code=200,
            response_body='{"status":"ok"}',
            accessible=True,
            error_message=''
        )
        
        self.assertEqual(result.endpoint, '/api/health')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.response_body, '{"status":"ok"}')
        self.assertTrue(result.accessible)
        self.assertEqual(result.error_message, '')
    
    def test_endpoint_result_failure(self):
        """Test creating EndpointResult for failed endpoint."""
        result = EndpointResult(
            endpoint='/api/health',
            status_code=None,
            response_body='',
            accessible=False,
            error_message='Connection refused'
        )
        
        self.assertEqual(result.endpoint, '/api/health')
        self.assertIsNone(result.status_code)
        self.assertEqual(result.response_body, '')
        self.assertFalse(result.accessible)
        self.assertEqual(result.error_message, 'Connection refused')
    
    def test_endpoint_results_creation(self):
        """Test creating EndpointResults with multiple results."""
        results = [
            EndpointResult('/', 200, '{"ok":true}', True, ''),
            EndpointResult('/api/health', 200, '{"healthy":true}', True, '')
        ]
        
        endpoint_results = EndpointResults(
            results=results,
            any_successful=True
        )
        
        self.assertEqual(len(endpoint_results.results), 2)
        self.assertTrue(endpoint_results.any_successful)
    
    def test_endpoint_results_defaults(self):
        """Test EndpointResults with default values."""
        endpoint_results = EndpointResults()
        
        self.assertEqual(len(endpoint_results.results), 0)
        self.assertFalse(endpoint_results.any_successful)


class TestFailureDiagnosis(unittest.TestCase):
    """Test cases for failure diagnosis logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.instance_name = "test-instance"
        self.region = "us-east-1"
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_instance_not_exists(self, mock_boto_client):
        """Test diagnosis when instance doesn't exist."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=False, state="not_found")
        ssh_status = SSHStatus(accessible=False)
        app_diagnostics = AppDiagnostics()
        endpoint_results = EndpointResults()
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "infrastructure_failure")
        self.assertIn("does not exist", diagnosis.root_cause)
        self.assertGreater(len(diagnosis.recommended_fixes), 0)
        self.assertGreaterEqual(diagnosis.confidence, 0.9)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_instance_not_running(self, mock_boto_client):
        """Test diagnosis when instance is not in running state."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=True, state="stopped", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=False)
        app_diagnostics = AppDiagnostics()
        endpoint_results = EndpointResults()
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "infrastructure_failure")
        self.assertIn("stopped", diagnosis.root_cause)
        self.assertIn("Start the instance", diagnosis.recommended_fixes[0])
        self.assertGreaterEqual(diagnosis.confidence, 0.85)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_ssh_failure(self, mock_boto_client):
        """Test diagnosis when SSH connection fails."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=False, error_message="Connection timeout")
        app_diagnostics = AppDiagnostics()
        endpoint_results = EndpointResults()
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "ssh_failure")
        self.assertIn("SSH connection", diagnosis.root_cause)
        self.assertIn("timeout", diagnosis.root_cause.lower())
        self.assertGreater(len(diagnosis.recommended_fixes), 0)
        self.assertGreaterEqual(diagnosis.confidence, 0.8)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_nodejs_not_installed(self, mock_boto_client):
        """Test diagnosis when Node.js is not installed."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(nodejs_version="not_installed")
        endpoint_results = EndpointResults()
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "dependency_failure")
        self.assertIn("Node.js is not installed", diagnosis.root_cause)
        self.assertIn("blueprint_id", diagnosis.recommended_fixes[1])
        self.assertGreaterEqual(diagnosis.confidence, 0.85)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_npm_not_installed(self, mock_boto_client):
        """Test diagnosis when npm is not installed."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(nodejs_version="v18.16.0", npm_installed=False)
        endpoint_results = EndpointResults()
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "dependency_failure")
        self.assertIn("npm is not installed", diagnosis.root_cause)
        self.assertGreater(len(diagnosis.recommended_fixes), 0)
        self.assertGreaterEqual(diagnosis.confidence, 0.8)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_pm2_not_available(self, mock_boto_client):
        """Test diagnosis when PM2 is not available."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(
            nodejs_version="v18.16.0",
            npm_installed=True,
            pm2_status="pm2_not_available"
        )
        endpoint_results = EndpointResults()
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "application_startup_failure")
        self.assertIn("PM2", diagnosis.root_cause)
        self.assertIn("Install PM2", diagnosis.recommended_fixes[0])
        self.assertGreaterEqual(diagnosis.confidence, 0.75)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_app_not_running(self, mock_boto_client):
        """Test diagnosis when application is not running under PM2."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(
            nodejs_version="v18.16.0",
            npm_installed=True,
            pm2_status="No processes running",
            app_logs="Error: Cannot find module 'express'"
        )
        endpoint_results = EndpointResults()
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "application_startup_failure")
        self.assertIn("not running", diagnosis.root_cause)
        self.assertIn("error", diagnosis.recommended_fixes[0].lower())
        self.assertGreaterEqual(diagnosis.confidence, 0.8)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_localhost_not_accessible(self, mock_boto_client):
        """Test diagnosis when application is not accessible on localhost."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(
            nodejs_version="v18.16.0",
            npm_installed=True,
            pm2_status="app online",
            localhost_accessible=False
        )
        endpoint_results = EndpointResults()
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "application_startup_failure")
        self.assertIn("not responding on localhost", diagnosis.root_cause)
        self.assertGreater(len(diagnosis.recommended_fixes), 0)
        self.assertGreaterEqual(diagnosis.confidence, 0.75)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_health_check_timeout(self, mock_boto_client):
        """Test diagnosis when health check endpoints timeout."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(
            nodejs_version="v18.16.0",
            npm_installed=True,
            pm2_status="app online",
            localhost_accessible=True
        )
        endpoint_results = EndpointResults(
            results=[
                EndpointResult('/api/health', None, '', False, 'Request timeout')
            ],
            any_successful=False
        )
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "health_check_failure")
        self.assertIn("timing out", diagnosis.root_cause)
        self.assertIn("firewall", diagnosis.recommended_fixes[0])
        self.assertGreaterEqual(diagnosis.confidence, 0.7)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_health_check_refused(self, mock_boto_client):
        """Test diagnosis when health check connection is refused."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(
            nodejs_version="v18.16.0",
            npm_installed=True,
            pm2_status="app online",
            localhost_accessible=True
        )
        endpoint_results = EndpointResults(
            results=[
                EndpointResult('/api/health', None, '', False, 'Connection refused')
            ],
            any_successful=False
        )
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "health_check_failure")
        self.assertIn("connection refused", diagnosis.root_cause)
        self.assertIn("0.0.0.0", diagnosis.recommended_fixes[0])
        self.assertGreaterEqual(diagnosis.confidence, 0.7)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_partial_endpoint_failure(self, mock_boto_client):
        """Test diagnosis when some endpoints succeed and some fail."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(
            nodejs_version="v18.16.0",
            npm_installed=True,
            pm2_status="app online",
            localhost_accessible=True
        )
        endpoint_results = EndpointResults(
            results=[
                EndpointResult('/', 200, '{"ok":true}', True, ''),
                EndpointResult('/api/health', 404, 'Not Found', True, 'HTTP 404')
            ],
            any_successful=True
        )
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "health_check_failure")
        self.assertIn("Some health check endpoints failed", diagnosis.root_cause)
        self.assertIn("/api/health", diagnosis.root_cause)
        self.assertGreaterEqual(diagnosis.confidence, 0.65)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_with_failure_point_ssh(self, mock_boto_client):
        """Test diagnosis using failure point from logs (SSH failure)."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        from log_retriever import FailurePoint
        failure_point = FailurePoint(
            job_name="post-steps-generic",
            step_name="Generic Application Deployment",
            error_message="SSH connection timeout",
            error_type="ssh_failure"
        )
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(
            nodejs_version="v18.16.0",
            npm_installed=True,
            pm2_status="app online",
            localhost_accessible=True
        )
        endpoint_results = EndpointResults(any_successful=True)
        
        # Act
        diagnosis = engine.diagnose_failure(
            failure_point, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "ssh_failure")
        self.assertIn("SSH connection failed in workflow", diagnosis.root_cause)
        self.assertGreater(len(diagnosis.recommended_fixes), 0)
        self.assertGreaterEqual(diagnosis.confidence, 0.75)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_with_failure_point_health_check(self, mock_boto_client):
        """Test diagnosis using failure point from logs (health check failure)."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        from log_retriever import FailurePoint
        failure_point = FailurePoint(
            job_name="verification",
            step_name="External Connectivity Test",
            error_message="Health check endpoint returned 404",
            error_type="health_check_failure"
        )
        
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(
            nodejs_version="v18.16.0",
            npm_installed=True,
            pm2_status="app online",
            localhost_accessible=True
        )
        endpoint_results = EndpointResults(any_successful=True)
        
        # Act
        diagnosis = engine.diagnose_failure(
            failure_point, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "health_check_failure")
        self.assertIn("Health check failed in workflow", diagnosis.root_cause)
        self.assertGreater(len(diagnosis.recommended_fixes), 0)
        self.assertGreaterEqual(diagnosis.confidence, 0.7)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_intermittent_failure(self, mock_boto_client):
        """Test diagnosis when all checks pass but workflow failed."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # All diagnostics show success
        instance_state = InstanceState(exists=True, state="running", public_ip="54.123.45.67")
        ssh_status = SSHStatus(accessible=True, connection_time=1.5)
        app_diagnostics = AppDiagnostics(
            nodejs_version="v18.16.0",
            npm_installed=True,
            pm2_status="app online",
            localhost_accessible=True
        )
        endpoint_results = EndpointResults(
            results=[EndpointResult('/', 200, '{"ok":true}', True, '')],
            any_successful=True
        )
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "intermittent_failure")
        self.assertIn("intermittent", diagnosis.root_cause)
        self.assertIn("timing", diagnosis.recommended_fixes[0].lower())
        self.assertGreaterEqual(diagnosis.confidence, 0.5)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_unknown_failure(self, mock_boto_client):
        """Test diagnosis when cause cannot be determined."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Minimal diagnostic data
        instance_state = None
        ssh_status = None
        app_diagnostics = None
        endpoint_results = None
        
        # Act
        diagnosis = engine.diagnose_failure(
            None, instance_state, ssh_status, app_diagnostics, endpoint_results
        )
        
        # Assert
        self.assertEqual(diagnosis.failure_type, "unknown_failure")
        self.assertIn("Unable to determine", diagnosis.root_cause)
        self.assertGreater(len(diagnosis.recommended_fixes), 0)
        self.assertLess(diagnosis.confidence, 0.6)
    
    @patch('diagnostic_engine.boto3.client')
    def test_diagnose_confidence_calculation(self, mock_boto_client):
        """Test that confidence scores are calculated appropriately."""
        # Arrange
        mock_lightsail = Mock()
        mock_boto_client.return_value = mock_lightsail
        
        engine = DiagnosticEngine(self.instance_name, self.region)
        
        # Test various scenarios and verify confidence is reasonable
        test_cases = [
            # (instance_exists, ssh_accessible, expected_min_confidence)
            (False, False, 0.9),  # Instance doesn't exist - high confidence
            (True, False, 0.8),   # SSH failure - high confidence
        ]
        
        for instance_exists, ssh_accessible, expected_min_conf in test_cases:
            instance_state = InstanceState(
                exists=instance_exists,
                state="running" if instance_exists else "not_found"
            )
            ssh_status = SSHStatus(accessible=ssh_accessible)
            
            diagnosis = engine.diagnose_failure(
                None, instance_state, ssh_status, AppDiagnostics(), EndpointResults()
            )
            
            self.assertGreaterEqual(
                diagnosis.confidence,
                expected_min_conf,
                f"Confidence too low for exists={instance_exists}, ssh={ssh_accessible}"
            )


class TestDiagnosis(unittest.TestCase):
    """Test cases for Diagnosis data class."""
    
    def test_diagnosis_creation(self):
        """Test creating Diagnosis with all fields."""
        diagnosis = Diagnosis(
            failure_type="ssh_failure",
            root_cause="SSH connection timeout",
            recommended_fixes=["Check firewall rules", "Verify instance is running"],
            confidence=0.85
        )
        
        self.assertEqual(diagnosis.failure_type, "ssh_failure")
        self.assertEqual(diagnosis.root_cause, "SSH connection timeout")
        self.assertEqual(len(diagnosis.recommended_fixes), 2)
        self.assertEqual(diagnosis.confidence, 0.85)
    
    def test_diagnosis_defaults(self):
        """Test Diagnosis with default values."""
        diagnosis = Diagnosis(
            failure_type="unknown",
            root_cause="Unknown error"
        )
        
        self.assertEqual(diagnosis.failure_type, "unknown")
        self.assertEqual(diagnosis.root_cause, "Unknown error")
        self.assertEqual(len(diagnosis.recommended_fixes), 0)
        self.assertEqual(diagnosis.confidence, 0.0)


if __name__ == '__main__':
    unittest.main()
