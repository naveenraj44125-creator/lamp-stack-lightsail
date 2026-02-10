"""
Diagnostic Engine module for analyzing Lightsail instance and application state.

This module provides functionality to:
- Check Lightsail instance state
- Test SSH connectivity
- Run application diagnostics
- Test health endpoints
- Diagnose failures based on collected data
"""

import boto3
import time
import subprocess
import tempfile
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class InstanceState:
    """Represents the state of a Lightsail instance."""
    exists: bool
    state: str  # running, stopped, pending, etc.
    public_ip: str = ""
    blueprint_id: str = ""


@dataclass
class SSHStatus:
    """Represents SSH connectivity status."""
    accessible: bool
    error_message: str = ""
    connection_time: float = 0.0


@dataclass
class AppDiagnostics:
    """Represents application diagnostic information."""
    nodejs_version: str = ""
    npm_installed: bool = False
    pm2_status: str = ""
    app_logs: str = ""
    localhost_accessible: bool = False


@dataclass
class EndpointResult:
    """Represents a single endpoint test result."""
    endpoint: str
    status_code: Optional[int]
    response_body: str
    accessible: bool
    error_message: str = ""


@dataclass
class EndpointResults:
    """Represents results from testing multiple endpoints."""
    results: List[EndpointResult] = field(default_factory=list)
    any_successful: bool = False


@dataclass
class Diagnosis:
    """Represents the diagnosis of a workflow failure."""
    failure_type: str
    root_cause: str
    recommended_fixes: List[str] = field(default_factory=list)
    confidence: float = 0.0


class DiagnosticEngine:
    """
    Runs diagnostic checks on Lightsail instance and application.
    
    This class performs various diagnostic operations to understand
    the state of the deployment and identify root causes of failures.
    """
    
    def __init__(self, instance_name: str, region: str = "us-east-1"):
        """
        Initialize with instance details.
        
        Args:
            instance_name: Name of the Lightsail instance
            region: AWS region (default: us-east-1)
        """
        self.instance_name = instance_name
        self.region = region
        self.lightsail_client = boto3.client('lightsail', region_name=region)
    
    def check_instance_state(self) -> InstanceState:
        """
        Check Lightsail instance state.
        
        Returns:
            InstanceState object with instance information
        """
        print(f"  Checking instance state for '{self.instance_name}'...")
        
        try:
            response = self.lightsail_client.get_instance(
                instanceName=self.instance_name
            )
            
            instance = response['instance']
            
            return InstanceState(
                exists=True,
                state=instance['state']['name'],
                public_ip=instance.get('publicIpAddress', ''),
                blueprint_id=instance.get('blueprintId', '')
            )
            
        except Exception as e:
            # Check if it's a NotFoundException by name
            if type(e).__name__ == 'NotFoundException':
                print(f"  Instance '{self.instance_name}' not found")
                return InstanceState(exists=False, state="not_found")
            
            # Generic error handling
            print(f"  Error checking instance state: {e}")
            return InstanceState(exists=False, state="error")
    
    def test_ssh_connectivity(self, max_retries: int = 3) -> SSHStatus:
        """
        Test SSH connection to instance with exponential backoff retry logic.
        
        Implements retry logic with exponential backoff:
        - Retry 1: immediate
        - Retry 2: wait 10 seconds
        - Retry 3: wait 20 seconds
        
        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            SSHStatus object with connectivity information
        """
        print(f"  Testing SSH connectivity to instance '{self.instance_name}'...")
        
        for attempt in range(max_retries):
            try:
                # Apply exponential backoff before retry (except first attempt)
                if attempt > 0:
                    wait_time = 10 * attempt  # 10s, 20s, 30s...
                    print(f"    Retry {attempt + 1}/{max_retries} after {wait_time}s wait...")
                    time.sleep(wait_time)
                
                # Record start time for connection timing
                start_time = time.time()
                
                # Get SSH access details from Lightsail
                ssh_response = self.lightsail_client.get_instance_access_details(
                    instanceName=self.instance_name
                )
                ssh_details = ssh_response['accessDetails']
                public_ip = ssh_details['ipAddress']
                
                print(f"    Attempting SSH connection to {public_ip}...")
                
                # Create temporary SSH key files
                key_path, cert_path = self._create_ssh_files(ssh_details)
                
                try:
                    # Build SSH command to test connectivity
                    ssh_cmd = [
                        'ssh', '-i', key_path, 
                        '-o', f'CertificateFile={cert_path}',
                        '-o', 'StrictHostKeyChecking=no',
                        '-o', 'UserKnownHostsFile=/dev/null',
                        '-o', 'ConnectTimeout=30',
                        '-o', 'BatchMode=yes',
                        '-o', 'IdentitiesOnly=yes',
                        f'{ssh_details["username"]}@{ssh_details["ipAddress"]}',
                        'echo "SSH test successful"'
                    ]
                    
                    # Execute SSH test command
                    result = subprocess.run(
                        ssh_cmd, 
                        capture_output=True, 
                        text=True, 
                        timeout=30
                    )
                    
                    connection_time = time.time() - start_time
                    
                    if result.returncode == 0:
                        print(f"    ✅ SSH connection successful (took {connection_time:.2f}s)")
                        return SSHStatus(
                            accessible=True,
                            error_message="",
                            connection_time=connection_time
                        )
                    else:
                        error_msg = result.stderr.strip() if result.stderr else "SSH connection failed"
                        print(f"    ❌ SSH connection failed: {error_msg}")
                        
                        # If this is not the last attempt, continue to retry
                        if attempt < max_retries - 1:
                            continue
                        
                        return SSHStatus(
                            accessible=False,
                            error_message=error_msg,
                            connection_time=connection_time
                        )
                        
                finally:
                    # Clean up temporary SSH files
                    self._cleanup_ssh_files(key_path, cert_path)
                    
            except subprocess.TimeoutExpired:
                error_msg = "SSH connection timeout (30s)"
                print(f"    ⏰ {error_msg}")
                
                if attempt < max_retries - 1:
                    continue
                    
                return SSHStatus(
                    accessible=False,
                    error_message=error_msg,
                    connection_time=30.0
                )
                
            except Exception as e:
                error_msg = str(e)
                print(f"    ❌ SSH test error: {error_msg}")
                
                # Check if it's a connection-related error that should be retried
                if attempt < max_retries - 1 and self._is_connection_error(error_msg):
                    continue
                
                return SSHStatus(
                    accessible=False,
                    error_message=error_msg,
                    connection_time=0.0
                )
        
        # Should not reach here, but return failure if we do
        return SSHStatus(
            accessible=False,
            error_message="Max retries exceeded",
            connection_time=0.0
        )
    
    def _create_ssh_files(self, ssh_details: Dict) -> tuple:
        """
        Create temporary SSH key files from Lightsail access details.
        
        Args:
            ssh_details: SSH access details from get_instance_access_details
            
        Returns:
            tuple: (key_path: str, cert_path: str)
        """
        import tempfile
        import os
        
        # Create private key file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as key_file:
            key_file.write(ssh_details['privateKey'])
            key_path = key_file.name
        
        # Create certificate file
        cert_path = key_path + '-cert.pub'
        cert_parts = ssh_details['certKey'].split(' ', 2)
        formatted_cert = f'{cert_parts[0]} {cert_parts[1]}\n' if len(cert_parts) >= 2 else ssh_details['certKey'] + '\n'
        
        with open(cert_path, 'w') as cert_file:
            cert_file.write(formatted_cert)
        
        # Set proper permissions
        os.chmod(key_path, 0o600)
        os.chmod(cert_path, 0o600)
        
        return key_path, cert_path
    
    def _cleanup_ssh_files(self, key_path: str, cert_path: str):
        """
        Clean up temporary SSH key files.
        
        Args:
            key_path: Path to private key file
            cert_path: Path to certificate file
        """
        import os
        
        try:
            if os.path.exists(key_path):
                os.unlink(key_path)
            if os.path.exists(cert_path):
                os.unlink(cert_path)
        except Exception:
            pass  # Ignore cleanup errors
    
    def _is_connection_error(self, error_msg: str) -> bool:
        """
        Check if error message indicates a connection issue that should be retried.
        
        Args:
            error_msg: Error message to check
            
        Returns:
            bool: True if error is connection-related, False otherwise
        """
        connection_errors = [
            'broken pipe', 'connection refused', 'connection timed out',
            'network unreachable', 'host unreachable', 'no route to host',
            'connection reset', 'connection closed by remote host',
            'ssh_exchange_identification', 'connection lost', 'connection aborted',
            'operation timed out', 'connect to host', 'timed out after'
        ]
        return any(phrase in error_msg.lower() for phrase in connection_errors)
    
    def run_application_diagnostics(self) -> AppDiagnostics:
        """
        Run Node.js/application diagnostics via SSH.
        
        Checks:
        - Node.js version
        - npm installation
        - PM2 process status
        - Application logs (last 50 lines)
        - Localhost accessibility
        
        Returns:
            AppDiagnostics object with application information
        """
        print(f"  Running application diagnostics on instance '{self.instance_name}'...")
        
        diagnostics = AppDiagnostics()
        
        try:
            # Get SSH access details
            ssh_response = self.lightsail_client.get_instance_access_details(
                instanceName=self.instance_name
            )
            ssh_details = ssh_response['accessDetails']
            
            # Create temporary SSH key files
            key_path, cert_path = self._create_ssh_files(ssh_details)
            
            try:
                # Check Node.js version
                print("    Checking Node.js version...")
                nodejs_version = self._run_ssh_command(
                    ssh_details, key_path, cert_path,
                    "node --version 2>/dev/null || echo 'not_installed'"
                )
                diagnostics.nodejs_version = nodejs_version.strip()
                
                # Check npm installation
                print("    Checking npm installation...")
                npm_check = self._run_ssh_command(
                    ssh_details, key_path, cert_path,
                    "which npm >/dev/null 2>&1 && echo 'installed' || echo 'not_installed'"
                )
                diagnostics.npm_installed = npm_check.strip() == 'installed'
                
                # Check PM2 status
                print("    Checking PM2 status...")
                pm2_status = self._run_ssh_command(
                    ssh_details, key_path, cert_path,
                    "pm2 list 2>/dev/null || echo 'pm2_not_available'"
                )
                diagnostics.pm2_status = pm2_status.strip()
                
                # Retrieve application logs
                print("    Retrieving application logs...")
                app_logs = self._run_ssh_command(
                    ssh_details, key_path, cert_path,
                    "pm2 logs --lines 50 --nostream 2>/dev/null || echo 'logs_not_available'"
                )
                diagnostics.app_logs = app_logs.strip()
                
                # Test localhost accessibility
                print("    Testing localhost accessibility...")
                localhost_test = self._run_ssh_command(
                    ssh_details, key_path, cert_path,
                    "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 2>/dev/null || echo 'failed'"
                )
                # Consider 200-399 as successful
                diagnostics.localhost_accessible = (
                    localhost_test.strip().isdigit() and 
                    200 <= int(localhost_test.strip()) < 400
                )
                
                print("    ✅ Application diagnostics completed")
                
            finally:
                # Clean up temporary SSH files
                self._cleanup_ssh_files(key_path, cert_path)
                
        except Exception as e:
            print(f"    ❌ Error running application diagnostics: {e}")
            # Return partial diagnostics with error information
            if not diagnostics.nodejs_version:
                diagnostics.nodejs_version = f"error: {str(e)}"
        
        return diagnostics
    
    def _run_ssh_command(self, ssh_details: Dict, key_path: str, cert_path: str, 
                        command: str, timeout: int = 30) -> str:
        """
        Execute a command via SSH and return the output.
        
        Args:
            ssh_details: SSH access details from get_instance_access_details
            key_path: Path to private key file
            cert_path: Path to certificate file
            command: Command to execute
            timeout: Command timeout in seconds (default: 30)
            
        Returns:
            str: Command output (stdout)
        """
        ssh_cmd = [
            'ssh', '-i', key_path,
            '-o', f'CertificateFile={cert_path}',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', f'ConnectTimeout={timeout}',
            '-o', 'BatchMode=yes',
            '-o', 'IdentitiesOnly=yes',
            '-o', 'LogLevel=ERROR',  # Suppress SSH warnings
            f'{ssh_details["username"]}@{ssh_details["ipAddress"]}',
            command
        ]
        
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return result.stdout if result.returncode == 0 else result.stderr
    
    def test_health_endpoints(self, public_ip: str, endpoints: List[str], 
                             port: int = 3000, max_retries: int = 10) -> EndpointResults:
        """
        Test health check endpoints with retry logic.
        
        Makes HTTP requests to configured endpoints with exponential backoff retry.
        Tests multiple endpoints (/, /api/health, /api/info, /api/metrics) and
        retries up to max_retries times with 15-second intervals.
        
        Args:
            public_ip: Public IP address of the instance
            endpoints: List of endpoint paths to test (e.g., ["/", "/api/health"])
            port: Port number (default: 3000)
            max_retries: Maximum number of retry attempts (default: 10)
            
        Returns:
            EndpointResults object with test results for each endpoint
        """
        print(f"  Testing health endpoints on {public_ip}:{port}...")
        
        results = []
        any_successful = False
        
        for endpoint in endpoints:
            print(f"    Testing endpoint: {endpoint}")
            endpoint_result = self._test_single_endpoint(
                public_ip, endpoint, port, max_retries
            )
            results.append(endpoint_result)
            
            if endpoint_result.accessible and endpoint_result.status_code == 200:
                any_successful = True
        
        return EndpointResults(
            results=results,
            any_successful=any_successful
        )
    
    def _test_single_endpoint(self, public_ip: str, endpoint: str, 
                             port: int, max_retries: int) -> EndpointResult:
        """
        Test a single health endpoint with retry logic.
        
        Implements retry logic with 15-second intervals between attempts.
        Uses curl for HTTP requests to avoid additional dependencies.
        
        Args:
            public_ip: Public IP address of the instance
            endpoint: Endpoint path to test (e.g., "/api/health")
            port: Port number
            max_retries: Maximum number of retry attempts
            
        Returns:
            EndpointResult object with test result
        """
        url = f"http://{public_ip}:{port}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                # Apply delay before retry (except first attempt)
                if attempt > 0:
                    wait_time = 15  # 15 seconds between retries
                    print(f"      Retry {attempt + 1}/{max_retries} after {wait_time}s wait...")
                    time.sleep(wait_time)
                
                # Use curl to make HTTP request
                # -s: silent mode
                # -w: write out format (status code)
                # -o: output file (we capture body separately)
                # --max-time: timeout in seconds
                # --connect-timeout: connection timeout
                curl_cmd = [
                    'curl', '-s',
                    '-w', '%{http_code}',
                    '-o', '-',  # Output body to stdout
                    '--max-time', '10',
                    '--connect-timeout', '5',
                    url
                ]
                
                result = subprocess.run(
                    curl_cmd,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                # Parse response: last 3 characters are status code
                output = result.stdout
                if len(output) >= 3:
                    # Extract status code from end of output
                    status_code_str = output[-3:]
                    response_body = output[:-3]
                    
                    try:
                        status_code = int(status_code_str)
                        
                        if status_code == 200:
                            print(f"      ✅ Endpoint accessible (HTTP {status_code})")
                            return EndpointResult(
                                endpoint=endpoint,
                                status_code=status_code,
                                response_body=response_body,
                                accessible=True,
                                error_message=""
                            )
                        else:
                            print(f"      ⚠️  Endpoint returned HTTP {status_code}")
                            
                            # If this is not the last attempt and it's a retriable error, continue
                            if attempt < max_retries - 1 and self._is_retriable_http_status(status_code):
                                continue
                            
                            return EndpointResult(
                                endpoint=endpoint,
                                status_code=status_code,
                                response_body=response_body,
                                accessible=True,  # Endpoint is accessible but returned non-200
                                error_message=f"HTTP {status_code}"
                            )
                    except ValueError:
                        # Could not parse status code
                        error_msg = "Invalid HTTP response"
                        print(f"      ❌ {error_msg}")
                        
                        if attempt < max_retries - 1:
                            continue
                        
                        return EndpointResult(
                            endpoint=endpoint,
                            status_code=None,
                            response_body=output,
                            accessible=False,
                            error_message=error_msg
                        )
                else:
                    # Empty or invalid response
                    error_msg = "Empty or invalid response"
                    print(f"      ❌ {error_msg}")
                    
                    if attempt < max_retries - 1:
                        continue
                    
                    return EndpointResult(
                        endpoint=endpoint,
                        status_code=None,
                        response_body=output,
                        accessible=False,
                        error_message=error_msg
                    )
                    
            except subprocess.TimeoutExpired:
                error_msg = "Request timeout (15s)"
                print(f"      ⏰ {error_msg}")
                
                if attempt < max_retries - 1:
                    continue
                
                return EndpointResult(
                    endpoint=endpoint,
                    status_code=None,
                    response_body="",
                    accessible=False,
                    error_message=error_msg
                )
                
            except Exception as e:
                error_msg = str(e)
                print(f"      ❌ Error: {error_msg}")
                
                # Check if it's a connection-related error that should be retried
                if attempt < max_retries - 1 and self._is_connection_error(error_msg):
                    continue
                
                return EndpointResult(
                    endpoint=endpoint,
                    status_code=None,
                    response_body="",
                    accessible=False,
                    error_message=error_msg
                )
        
        # Should not reach here, but return failure if we do
        return EndpointResult(
            endpoint=endpoint,
            status_code=None,
            response_body="",
            accessible=False,
            error_message="Max retries exceeded"
        )
    
    def _is_retriable_http_status(self, status_code: int) -> bool:
        """
        Check if HTTP status code indicates a retriable error.
        
        Args:
            status_code: HTTP status code
            
        Returns:
            bool: True if status should be retried, False otherwise
        """
        # Retry on server errors (5xx) and service unavailable (503)
        # Also retry on 502 (Bad Gateway) and 504 (Gateway Timeout)
        retriable_codes = [500, 502, 503, 504]
        return status_code in retriable_codes
    
    def diagnose_failure(self, failure_point, instance_state: InstanceState,
                        ssh_status: SSHStatus, app_diagnostics: AppDiagnostics,
                        endpoint_results: EndpointResults) -> Diagnosis:
        """
        Diagnose failure based on collected diagnostic data.
        
        Analyzes all collected diagnostic data to determine the root cause of the
        deployment failure. Classifies failures into categories and provides
        actionable recommended fixes with confidence scores.
        
        Args:
            failure_point: FailurePoint from log analysis (can be None)
            instance_state: Instance state information
            ssh_status: SSH connectivity status
            app_diagnostics: Application diagnostic information
            endpoint_results: Health endpoint test results
            
        Returns:
            Diagnosis object with failure type, root cause, recommended fixes,
            and confidence score (0.0-1.0)
        """
        print("  Analyzing diagnostic data...")
        
        # Initialize diagnosis components
        failure_type = "unknown_failure"
        root_cause = ""
        recommended_fixes = []
        confidence = 0.0
        
        # Track available diagnostic data for confidence calculation
        data_points = 0
        max_data_points = 5  # instance, ssh, app, endpoints, failure_point
        
        # Check instance state
        if instance_state:
            data_points += 1
            if not instance_state.exists:
                failure_type = "infrastructure_failure"
                root_cause = "Lightsail instance does not exist or was not created successfully"
                recommended_fixes = [
                    "Verify AWS credentials and permissions",
                    "Check CloudFormation/Terraform logs for instance creation errors",
                    "Verify instance name in deployment configuration",
                    "Check AWS service limits for Lightsail instances in the region"
                ]
                confidence = 0.95
                print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
                return Diagnosis(
                    failure_type=failure_type,
                    root_cause=root_cause,
                    recommended_fixes=recommended_fixes,
                    confidence=confidence
                )
            elif instance_state.state != "running":
                failure_type = "infrastructure_failure"
                root_cause = f"Lightsail instance exists but is in '{instance_state.state}' state (expected: running)"
                recommended_fixes = [
                    f"Start the instance if it's in 'stopped' state",
                    "Wait for instance to finish starting if it's in 'pending' state",
                    "Check AWS console for instance status and any error messages",
                    "Verify instance has not been terminated or is being terminated"
                ]
                confidence = 0.90
                print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
                return Diagnosis(
                    failure_type=failure_type,
                    root_cause=root_cause,
                    recommended_fixes=recommended_fixes,
                    confidence=confidence
                )
        
        # Check SSH connectivity
        if ssh_status:
            data_points += 1
            if not ssh_status.accessible:
                failure_type = "ssh_failure"
                root_cause = f"SSH connection to instance failed: {ssh_status.error_message}"
                recommended_fixes = [
                    "Verify instance is in 'running' state",
                    "Check security group/firewall rules allow SSH (port 22)",
                    "Verify SSH key permissions are correct (600)",
                    "Wait for instance to fully boot (may take 2-3 minutes after 'running' state)",
                    "Check if instance has a public IP address assigned"
                ]
                
                # Add specific fixes based on error message
                error_lower = ssh_status.error_message.lower()
                if "timeout" in error_lower:
                    recommended_fixes.insert(0, "SSH connection timed out - instance may not be fully booted or network is unreachable")
                elif "refused" in error_lower:
                    recommended_fixes.insert(0, "SSH connection refused - SSH service may not be running on instance")
                elif "authentication" in error_lower or "permission" in error_lower:
                    recommended_fixes.insert(0, "SSH authentication failed - verify SSH key is correct")
                
                confidence = 0.85
                print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
                return Diagnosis(
                    failure_type=failure_type,
                    root_cause=root_cause,
                    recommended_fixes=recommended_fixes,
                    confidence=confidence
                )
        
        # Check application diagnostics (requires SSH to be working)
        if app_diagnostics:
            data_points += 1
            
            # Check if Node.js is installed
            if not app_diagnostics.nodejs_version or "not_installed" in app_diagnostics.nodejs_version:
                failure_type = "dependency_failure"
                root_cause = "Node.js is not installed on the instance"
                recommended_fixes = [
                    "Verify deployment script includes Node.js installation",
                    "Check blueprint_id uses correct format (e.g., 'ubuntu-22-04' not 'ubuntu_22_04')",
                    "Manually install Node.js: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs",
                    "Verify pre-deployment steps completed successfully"
                ]
                confidence = 0.90
                print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
                return Diagnosis(
                    failure_type=failure_type,
                    root_cause=root_cause,
                    recommended_fixes=recommended_fixes,
                    confidence=confidence
                )
            
            # Check if npm is installed
            if not app_diagnostics.npm_installed:
                failure_type = "dependency_failure"
                root_cause = "npm is not installed on the instance"
                recommended_fixes = [
                    "npm should be installed with Node.js - verify Node.js installation is complete",
                    "Manually install npm: sudo apt-get install -y npm",
                    "Check if Node.js installation script completed successfully"
                ]
                confidence = 0.85
                print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
                return Diagnosis(
                    failure_type=failure_type,
                    root_cause=root_cause,
                    recommended_fixes=recommended_fixes,
                    confidence=confidence
                )
            
            # Check PM2 status
            if "pm2_not_available" in app_diagnostics.pm2_status:
                failure_type = "application_startup_failure"
                root_cause = "PM2 process manager is not installed or not in PATH"
                recommended_fixes = [
                    "Install PM2 globally: sudo npm install -g pm2",
                    "Verify deployment script includes PM2 installation",
                    "Check if npm global packages are in PATH"
                ]
                confidence = 0.80
                print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
                return Diagnosis(
                    failure_type=failure_type,
                    root_cause=root_cause,
                    recommended_fixes=recommended_fixes,
                    confidence=confidence
                )
            elif "online" not in app_diagnostics.pm2_status.lower() and app_diagnostics.pm2_status:
                # PM2 is available but no processes are running or they're not online
                failure_type = "application_startup_failure"
                root_cause = "Application is not running under PM2 or has crashed"
                recommended_fixes = [
                    "Check PM2 logs for startup errors: pm2 logs",
                    "Verify application entry point is correct (e.g., server.js, index.js)",
                    "Check application logs for errors",
                    "Manually start application: pm2 start <entry-point>",
                    "Verify package.json has correct start script"
                ]
                
                # Add specific fixes based on logs if available
                if app_diagnostics.app_logs and "error" in app_diagnostics.app_logs.lower():
                    recommended_fixes.insert(0, "Application logs show errors - review logs for specific error messages")
                
                confidence = 0.85
                print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
                return Diagnosis(
                    failure_type=failure_type,
                    root_cause=root_cause,
                    recommended_fixes=recommended_fixes,
                    confidence=confidence
                )
            
            # Check localhost accessibility
            if not app_diagnostics.localhost_accessible:
                failure_type = "application_startup_failure"
                root_cause = "Application is not responding on localhost (port 3000)"
                recommended_fixes = [
                    "Verify application is running: pm2 list",
                    "Check if application is listening on correct port (3000)",
                    "Review application logs for startup errors: pm2 logs",
                    "Verify application configuration (PORT environment variable)",
                    "Check if port is already in use: sudo lsof -i :3000"
                ]
                confidence = 0.80
                print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
                return Diagnosis(
                    failure_type=failure_type,
                    root_cause=root_cause,
                    recommended_fixes=recommended_fixes,
                    confidence=confidence
                )
        
        # Check health endpoint results
        if endpoint_results:
            data_points += 1
            if not endpoint_results.any_successful:
                # Application is running locally but not accessible externally
                failure_type = "health_check_failure"
                
                # Analyze endpoint results for more specific diagnosis
                all_timeout = all(
                    "timeout" in r.error_message.lower() 
                    for r in endpoint_results.results 
                    if r.error_message
                )
                all_refused = all(
                    "refused" in r.error_message.lower() 
                    for r in endpoint_results.results 
                    if r.error_message
                )
                
                if all_timeout:
                    root_cause = "Health check endpoints are timing out - firewall may be blocking external access"
                    recommended_fixes = [
                        "Verify firewall rules allow traffic on application port (default: 3000)",
                        "Check deployment configuration: allowed_ports should include application port",
                        "Verify security group allows inbound traffic on application port",
                        "Check if application is bound to localhost only (should bind to 0.0.0.0)"
                    ]
                elif all_refused:
                    root_cause = "Health check endpoints connection refused - application may not be listening on external interface"
                    recommended_fixes = [
                        "Verify application is bound to 0.0.0.0 (not 127.0.0.1 or localhost)",
                        "Check application configuration for host/bind address",
                        "Verify application is running: pm2 list",
                        "Check firewall rules allow traffic on application port"
                    ]
                else:
                    root_cause = "Health check endpoints are not accessible from external network"
                    recommended_fixes = [
                        "Verify application is running and accessible on localhost",
                        "Check firewall rules allow traffic on application port",
                        "Verify application is bound to 0.0.0.0 (not localhost)",
                        "Check if health check endpoint exists in application code",
                        "Verify port configuration matches between deployment config and application"
                    ]
                
                confidence = 0.75
                print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
                return Diagnosis(
                    failure_type=failure_type,
                    root_cause=root_cause,
                    recommended_fixes=recommended_fixes,
                    confidence=confidence
                )
            else:
                # Some endpoints succeeded - check for partial failures
                failed_endpoints = [
                    r for r in endpoint_results.results 
                    if not r.accessible or r.status_code != 200
                ]
                if failed_endpoints:
                    failure_type = "health_check_failure"
                    failed_paths = [r.endpoint for r in failed_endpoints]
                    root_cause = f"Some health check endpoints failed: {', '.join(failed_paths)}"
                    recommended_fixes = [
                        "Verify all health check endpoints exist in application code",
                        "Check application routing configuration",
                        "Review application logs for endpoint-specific errors",
                        "Verify endpoint paths match deployment configuration"
                    ]
                    confidence = 0.70
                    print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
                    return Diagnosis(
                        failure_type=failure_type,
                        root_cause=root_cause,
                        recommended_fixes=recommended_fixes,
                        confidence=confidence
                    )
        
        # Use failure point from logs if available
        if failure_point:
            data_points += 1
            
            # Map error types to failure classifications
            if failure_point.error_type == "ssh_failure":
                failure_type = "ssh_failure"
                root_cause = f"SSH connection failed in workflow: {failure_point.error_message}"
                recommended_fixes = [
                    "Verify instance is fully booted before SSH attempts",
                    "Increase SSH connection timeout in workflow",
                    "Check security group/firewall rules",
                    "Verify SSH key configuration in workflow"
                ]
                confidence = 0.80
            elif failure_point.error_type == "health_check_failure":
                failure_type = "health_check_failure"
                root_cause = f"Health check failed in workflow: {failure_point.error_message}"
                recommended_fixes = [
                    "Verify application started successfully before health checks",
                    "Increase health check timeout/retries in workflow",
                    "Check application logs for startup errors",
                    "Verify health check endpoint exists and returns 200"
                ]
                confidence = 0.75
            elif failure_point.error_type == "dependency_failure":
                failure_type = "dependency_failure"
                root_cause = f"Dependency installation failed: {failure_point.error_message}"
                recommended_fixes = [
                    "Check npm install logs for specific errors",
                    "Verify package.json is valid",
                    "Check for network connectivity issues during npm install",
                    "Verify Node.js version is compatible with dependencies"
                ]
                confidence = 0.85
            elif failure_point.error_type == "application_startup_failure":
                failure_type = "application_startup_failure"
                root_cause = f"Application startup failed: {failure_point.error_message}"
                recommended_fixes = [
                    "Review application logs for startup errors",
                    "Verify application entry point is correct",
                    "Check environment variables are set correctly",
                    "Verify all dependencies are installed"
                ]
                confidence = 0.80
            else:
                failure_type = "unknown_failure"
                root_cause = f"Workflow failed at {failure_point.job_name}/{failure_point.step_name}: {failure_point.error_message}"
                recommended_fixes = [
                    "Review workflow logs for detailed error messages",
                    "Check all diagnostic data for clues",
                    "Verify deployment configuration is correct",
                    "Try running deployment steps manually to isolate issue"
                ]
                confidence = 0.50
            
            print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
            return Diagnosis(
                failure_type=failure_type,
                root_cause=root_cause,
                recommended_fixes=recommended_fixes,
                confidence=confidence
            )
        
        # If we reach here, we have some data but no clear failure
        # Calculate confidence based on available data
        confidence = data_points / max_data_points * 0.5  # Max 0.5 for unclear diagnosis
        
        # Check if everything appears to be working
        if (instance_state and instance_state.exists and instance_state.state == "running" and
            ssh_status and ssh_status.accessible and
            endpoint_results and endpoint_results.any_successful):
            failure_type = "intermittent_failure"
            root_cause = "All diagnostic checks passed - failure may be intermittent or timing-related"
            recommended_fixes = [
                "Review workflow logs for timing issues",
                "Increase timeouts in workflow configuration",
                "Check for race conditions in deployment process",
                "Verify health checks are not running before application is ready"
            ]
            confidence = 0.60
        else:
            failure_type = "unknown_failure"
            root_cause = "Unable to determine root cause from available diagnostic data"
            recommended_fixes = [
                "Collect more diagnostic data",
                "Review workflow logs manually",
                "Check AWS CloudWatch logs",
                "Verify all deployment steps completed successfully"
            ]
        
        print(f"    Diagnosis: {failure_type} (confidence: {confidence:.2f})")
        return Diagnosis(
            failure_type=failure_type,
            root_cause=root_cause,
            recommended_fixes=recommended_fixes,
            confidence=confidence
        )
