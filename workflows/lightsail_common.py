#!/usr/bin/env python3
"""
Common utilities for AWS Lightsail deployment workflows
This module provides shared functionality for SSH connections, file operations, and AWS client management
"""

import boto3
import subprocess
import tempfile
import os
import time
import sys
import socket
from botocore.exceptions import ClientError, NoCredentialsError

class LightsailBase:
    """Base class for Lightsail operations with common SSH and AWS functionality"""
    
    def __init__(self, instance_name, region='us-east-1'):
        self.instance_name = instance_name
        self.region = region
        try:
            self.lightsail = boto3.client('lightsail', region_name=region)
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure AWS credentials.")
            sys.exit(1)
    
    def run_command(self, command, timeout=300, max_retries=1, show_output_lines=20, verbose=False):
        """
        Execute command on Lightsail instance using get_instance_access_details
        
        Args:
            command (str): Command to execute
            timeout (int): Command timeout in seconds
            max_retries (int): Maximum number of retry attempts
            show_output_lines (int): Number of output lines to display
            verbose (bool): Show detailed command execution
            
        Returns:
            tuple: (success: bool, output: str)
        """
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 Retry attempt {attempt + 1}/{max_retries}")
                    # Progressive backoff with longer initial waits for GitHub Actions
                    wait_time = min(15 + (attempt * 10), 60)
                    print(f"   ⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    
                    # Test connectivity before retry
                    if not self.test_network_connectivity():
                        print("   ⚠️ Network connectivity still failing, continuing retry...")
                
                # Show command being executed
                if verbose or "GITHUB_ACTIONS" in os.environ:
                    print(f"🔧 Executing command on {self.instance_name}:")
                    # Show first few lines of the command for context
                    cmd_lines = command.split('\n')
                    for i, line in enumerate(cmd_lines[:5]):
                        if line.strip():
                            print(f"   {i+1}: {line.strip()}")
                    if len(cmd_lines) > 5:
                        print(f"   ... ({len(cmd_lines)-5} more lines)")
                else:
                    print(f"🔧 Running: {command[:100]}{'...' if len(command) > 100 else ''}")
                
                # Get SSH access details
                ssh_response = self.lightsail.get_instance_access_details(instanceName=self.instance_name)
                ssh_details = ssh_response['accessDetails']
                
                # Create temporary SSH key files
                key_path, cert_path = self.create_ssh_files(ssh_details)
                
                try:
                    ssh_cmd = self._build_ssh_command(key_path, cert_path, ssh_details, command)
                    
                    # Show SSH command in verbose mode
                    if verbose or "GITHUB_ACTIONS" in os.environ:
                        print(f"📡 SSH Command: ssh {ssh_details['username']}@{ssh_details['ipAddress']}")
                    
                    result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
                    
                    if result.returncode == 0:
                        print(f"   ✅ Success (exit code: 0)")
                        if result.stdout.strip():
                            if verbose or "GITHUB_ACTIONS" in os.environ:
                                print(f"   📤 Output:")
                                self._display_detailed_output(result.stdout.strip(), show_output_lines)
                            else:
                                self._display_output(result.stdout.strip(), show_output_lines)
                        return True, result.stdout.strip()
                    else:
                        error_msg = result.stderr.strip()
                        print(f"   ❌ Failed (exit code: {result.returncode})")
                        if error_msg:
                            print(f"   📤 Error Output:")
                            self._display_detailed_output(error_msg, show_output_lines)
                        if result.stdout.strip():
                            print(f"   📤 Standard Output:")
                            self._display_detailed_output(result.stdout.strip(), show_output_lines)
                        
                        # Check if it's a connection issue that we should retry
                        if max_retries > 1 and self._is_connection_error(error_msg):
                            if attempt < max_retries - 1:
                                print(f"   🔄 Connection issue detected, will retry...")
                                # For GitHub Actions, try to restart instance on persistent failures
                                if attempt >= 3 and "GITHUB_ACTIONS" in os.environ:
                                    print("   🔄 GitHub Actions detected - attempting instance restart...")
                                    self.restart_instance_for_connectivity()
                                continue
                        
                        return False, error_msg
                    
                finally:
                    self._cleanup_ssh_files(key_path, cert_path)
                    
            except subprocess.TimeoutExpired:
                print(f"   ⏰ Command timed out after {timeout} seconds")
                if attempt < max_retries - 1:
                    print(f"   🔄 Will retry...")
                    continue
                return False, f"Command timed out after {timeout} seconds"
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Error: {error_msg}")
                
                # Check if it's a connection issue that we should retry
                if max_retries > 1 and self._is_connection_error(error_msg):
                    if attempt < max_retries - 1:
                        print(f"   🔄 Connection issue detected, will retry...")
                        continue
                
                return False, error_msg
        
        return False, "Max retries exceeded"

    def create_ssh_files(self, ssh_details):
        """
        Create temporary SSH key files from Lightsail access details
        
        Args:
            ssh_details (dict): SSH access details from get_instance_access_details
            
        Returns:
            tuple: (key_path: str, cert_path: str)
        """
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

    def copy_file_to_instance(self, local_path, remote_path, timeout=300):
        """
        Copy file to instance using SCP
        
        Args:
            local_path (str): Local file path
            remote_path (str): Remote file path
            timeout (int): Transfer timeout in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"📤 Copying {local_path} to {remote_path}")
            
            ssh_response = self.lightsail.get_instance_access_details(instanceName=self.instance_name)
            ssh_details = ssh_response['accessDetails']
            
            key_path, cert_path = self.create_ssh_files(ssh_details)
            
            try:
                scp_cmd = [
                    'scp', '-i', key_path, '-o', f'CertificateFile={cert_path}',
                    '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'ConnectTimeout=30', '-o', 'IdentitiesOnly=yes',
                    local_path, f'{ssh_details["username"]}@{ssh_details["ipAddress"]}:{remote_path}'
                ]
                
                result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=timeout)
                
                if result.returncode == 0:
                    print(f"   ✅ File copied successfully")
                    return True
                else:
                    print(f"   ❌ Failed to copy file (exit code: {result.returncode})")
                    if result.stderr.strip():
                        print(f"   Error: {result.stderr.strip()}")
                    return False
                
            finally:
                self._cleanup_ssh_files(key_path, cert_path)
                
        except Exception as e:
            print(f"   ❌ Error copying file: {str(e)}")
            return False

    def get_instance_info(self):
        """
        Get instance information including public IP and state
        
        Returns:
            dict: Instance information or None if error
        """
        try:
            response = self.lightsail.get_instance(instanceName=self.instance_name)
            instance = response['instance']
            return {
                'name': instance['name'],
                'state': instance['state']['name'],
                'public_ip': instance.get('publicIpAddress'),
                'private_ip': instance.get('privateIpAddress'),
                'blueprint': instance.get('blueprintName'),
                'bundle': instance.get('bundleId')
            }
        except ClientError as e:
            print(f"❌ Error getting instance info: {e}")
            return None

    def wait_for_instance_state(self, target_state='running', timeout=300):
        """
        Wait for instance to reach target state
        
        Args:
            target_state (str): Target instance state
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if target state reached, False otherwise
        """
        print(f"⏳ Waiting for instance {self.instance_name} to be {target_state}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.lightsail.get_instance(instanceName=self.instance_name)
                current_state = response['instance']['state']['name']
                print(f"Instance state: {current_state}")
                
                if current_state == target_state:
                    print(f"✅ Instance is {target_state}")
                    return True
                elif current_state in ['stopped', 'stopping', 'terminated'] and target_state == 'running':
                    print(f"❌ Instance is in {current_state} state")
                    return False
                    
                time.sleep(10)
            except ClientError as e:
                print(f"❌ Error checking instance state: {e}")
                return False
        
        print(f"❌ Timeout waiting for instance to be {target_state}")
        return False

    def test_ssh_connectivity(self, timeout=30, max_retries=3):
        """
        Test SSH connectivity to the instance
        
        Args:
            timeout (int): Connection timeout
            max_retries (int): Maximum retry attempts
            
        Returns:
            bool: True if SSH is accessible, False otherwise
        """
        print("🔍 Testing SSH connectivity...")
        success, _ = self.run_command("echo 'SSH test successful'", timeout=timeout, max_retries=max_retries)
        if success:
            print("✅ SSH connectivity confirmed")
        else:
            print("❌ SSH connectivity failed")
        return success

    def test_network_connectivity(self):
        """Test network connectivity to the instance"""
        try:
            ssh_response = self.lightsail.get_instance_access_details(instanceName=self.instance_name)
            ip_address = ssh_response['accessDetails']['ipAddress']
            
            print(f"🔍 Testing network connectivity to {ip_address}...")
            
            # Test basic connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((ip_address, 22))
            sock.close()
            
            if result == 0:
                print("✅ Network connectivity to SSH port successful")
                return True
            else:
                print(f"⚠️ Network connectivity test failed (error code: {result})")
                return False
                
        except Exception as e:
            print(f"⚠️ Network connectivity test error: {e}")
            return False

    def restart_instance_for_connectivity(self):
        """Restart instance to resolve connectivity issues (GitHub Actions fallback)"""
        try:
            print("🔄 Attempting instance restart to resolve connectivity...")
            
            # Stop instance
            self.lightsail.stop_instance(instanceName=self.instance_name)
            print("   ⏳ Stopping instance...")
            time.sleep(30)
            
            # Wait for stopped state
            for _ in range(12):  # 2 minutes max
                response = self.lightsail.get_instance(instanceName=self.instance_name)
                state = response['instance']['state']['name']
                if state == 'stopped':
                    break
                time.sleep(10)
            
            # Start instance
            self.lightsail.start_instance(instanceName=self.instance_name)
            print("   ⏳ Starting instance...")
            time.sleep(60)
            
            # Wait for running state
            for _ in range(18):  # 3 minutes max
                response = self.lightsail.get_instance(instanceName=self.instance_name)
                state = response['instance']['state']['name']
                if state == 'running':
                    print("   ✅ Instance restarted successfully")
                    time.sleep(30)  # Additional wait for SSH service
                    return True
                time.sleep(10)
                
            print("   ⚠️ Instance restart timeout")
            return False
            
        except Exception as e:
            print(f"   ❌ Instance restart failed: {e}")
            return False

    def _build_ssh_command(self, key_path, cert_path, ssh_details, command):
        """Build SSH command with proper options"""
        # Enhanced SSH configuration for GitHub Actions compatibility
        if "GITHUB_ACTIONS" in os.environ:
            return [
                'ssh', '-i', key_path, '-o', f'CertificateFile={cert_path}',
                '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'ConnectTimeout=60', '-o', 'ServerAliveInterval=30',
                '-o', 'ServerAliveCountMax=6', '-o', 'ConnectionAttempts=3',
                '-o', 'IdentitiesOnly=yes', '-o', 'TCPKeepAlive=yes',
                '-o', 'ExitOnForwardFailure=yes', '-o', 'BatchMode=yes',
                '-o', 'PreferredAuthentications=publickey', '-o', 'LogLevel=VERBOSE',
                f'{ssh_details["username"]}@{ssh_details["ipAddress"]}', command
            ]
        else:
            return [
                'ssh', '-i', key_path, '-o', f'CertificateFile={cert_path}',
                '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'ConnectTimeout=30', '-o', 'ServerAliveInterval=10',
                '-o', 'ServerAliveCountMax=3', '-o', 'IdentitiesOnly=yes',
                '-o', 'BatchMode=yes', '-o', 'LogLevel=ERROR',
                f'{ssh_details["username"]}@{ssh_details["ipAddress"]}', command
            ]

    def _display_output(self, output, max_lines):
        """Display command output with line limit"""
        lines = output.split('\n')
        for line in lines[:max_lines]:
            print(f"   {line}")
        if len(lines) > max_lines:
            print(f"   ... ({len(lines) - max_lines} more lines)")
    
    def _display_detailed_output(self, output, max_lines):
        """Display command output with detailed formatting for GitHub Actions"""
        lines = output.split('\n')
        for i, line in enumerate(lines[:max_lines], 1):
            if line.strip():
                print(f"   {i:3d}: {line}")
            else:
                print(f"   {i:3d}:")
        if len(lines) > max_lines:
            print(f"   ... ({len(lines) - max_lines} more lines truncated)")
    
    def run_command_with_live_output(self, command, timeout=300):
        """
        Execute command with live output streaming - shows each command as it executes
        """
        print(f"🔧 Executing with live output on {self.instance_name}:")
        
        # Break down complex scripts into individual commands
        if 'set -e' in command and '\n' in command:
            return self._run_script_with_individual_commands(command, timeout)
        else:
            return self.run_command(command, timeout, verbose=True)

    def _is_connection_error(self, error_msg):
        """Check if error message indicates a connection issue"""
        connection_errors = [
            'broken pipe', 'connection refused', 'connection timed out', 
            'network unreachable', 'host unreachable', 'no route to host',
            'connection reset', 'connection closed by remote host',
            'ssh_exchange_identification', 'connection lost', 'connection aborted',
            'operation timed out', 'connect to host', 'timed out after'
        ]
        return any(phrase in error_msg.lower() for phrase in connection_errors)

    def _cleanup_ssh_files(self, key_path, cert_path):
        """Clean up temporary SSH key files"""
        try:
            if os.path.exists(key_path):
                os.unlink(key_path)
            if os.path.exists(cert_path):
                os.unlink(cert_path)
        except Exception:
            pass  # Ignore cleanup errors
    
    def _run_script_with_individual_commands(self, script, timeout=300):
        """
        Run a bash script by executing individual commands and showing each one
        """
        print("📋 Breaking down script into individual commands:")
        
        # Parse the script into individual commands
        lines = script.split('\n')
        commands = []
        current_command = []
        in_heredoc = False
        heredoc_delimiter = None
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines and comments at the start
            if not stripped or stripped.startswith('#'):
                if current_command:  # Only add if we're building a command
                    current_command.append(line)
                continue
            
            # Skip 'set -e' as it's just error handling
            if stripped == 'set -e':
                continue
            
            # Handle heredoc start
            if '<<' in line and not in_heredoc:
                heredoc_delimiter = line.split('<<')[-1].strip().strip("'\"")
                current_command.append(line)
                in_heredoc = True
                continue
            
            # Handle heredoc end
            if in_heredoc:
                current_command.append(line)
                if stripped == heredoc_delimiter or stripped.endswith(heredoc_delimiter):
                    in_heredoc = False
                    heredoc_delimiter = None
                continue
            
            # Handle line continuations
            if line.endswith('\\'):
                current_command.append(line)
                continue
            
            # Add current line to command
            current_command.append(line)
            
            # If this looks like a complete command, save it
            if (stripped.endswith(';') or 
                not stripped.endswith('\\') and 
                not stripped.endswith('|') and
                not stripped.endswith('&&') and
                not stripped.endswith('||')):
                
                if current_command:
                    cmd_text = '\n'.join(current_command).strip()
                    if cmd_text and not cmd_text.startswith('#'):
                        commands.append(cmd_text)
                current_command = []
        
        # Add any remaining command
        if current_command:
            cmd_text = '\n'.join(current_command).strip()
            if cmd_text and not cmd_text.startswith('#'):
                commands.append(cmd_text)
        
        print(f"   📊 Found {len(commands)} individual commands to execute")
        
        # Execute each command individually
        all_output = []
        for i, cmd in enumerate(commands, 1):
            print(f"\n   🔸 Command {i}/{len(commands)}:")
            
            # Show the command being executed
            cmd_lines = cmd.split('\n')
            for j, cmd_line in enumerate(cmd_lines):
                if cmd_line.strip():
                    print(f"      {j+1}: {cmd_line.strip()}")
            
            # Execute the command
            success, output = self.run_command(cmd, timeout=60, verbose=False)
            
            if success:
                print(f"      ✅ Command {i} completed successfully")
                if output.strip():
                    # Show key output lines
                    output_lines = output.split('\n')
                    for line in output_lines[:10]:  # Show first 10 lines
                        if line.strip():
                            print(f"         {line}")
                    if len(output_lines) > 10:
                        print(f"         ... ({len(output_lines)-10} more lines)")
                all_output.append(output)
            else:
                print(f"      ❌ Command {i} failed")
                if output:
                    print(f"         Error: {output}")
                return False, f"Command {i} failed: {output}"
        
        return True, '\n'.join(all_output)


class LightsailSSHManager(LightsailBase):
    """Enhanced SSH manager with additional connectivity features"""
    
    def wait_for_ssh_ready(self, timeout=300):
        """
        Wait for instance to be running and SSH to be ready
        
        Args:
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if SSH is ready, False otherwise
        """
        # First wait for instance to be running
        if not self.wait_for_instance_state('running', timeout):
            return False
        
        # Wait additional time for SSH service to start
        print("⏳ Waiting for SSH service to be ready...")
        time.sleep(30)  # Give SSH service time to start
        
        # Test SSH connectivity with retries
        return self.test_ssh_connectivity(timeout=30, max_retries=3)


def create_lightsail_client(instance_name, region='us-east-1', client_type='base'):
    """
    Factory function to create appropriate Lightsail client
    
    Args:
        instance_name (str): Lightsail instance name
        region (str): AWS region
        client_type (str): Type of client ('base', 'ssh')
        
    Returns:
        LightsailBase or LightsailSSHManager: Configured client instance
    """
    if client_type == 'ssh':
        return LightsailSSHManager(instance_name, region)
    else:
        return LightsailBase(instance_name, region)
