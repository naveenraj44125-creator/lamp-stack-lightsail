"""
Log Retriever module for fetching and parsing GitHub Actions workflow logs.

This module provides functionality to:
- Retrieve workflow logs using GitHub CLI
- Parse logs into structured format
- Identify failure points
- Extract error messages
"""

import subprocess
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class StepLog:
    """Represents a single step within a job."""
    name: str
    status: str
    output: str


@dataclass
class JobLog:
    """Represents a single job within a workflow."""
    name: str
    status: str
    steps: List[StepLog] = field(default_factory=list)


@dataclass
class WorkflowLogs:
    """Represents complete workflow logs."""
    jobs: Dict[str, JobLog] = field(default_factory=dict)
    overall_status: str = "unknown"
    conclusion: str = "unknown"


@dataclass
class FailurePoint:
    """Represents the specific point where a workflow failed."""
    job_name: str
    step_name: str
    error_message: str
    error_type: str  # ssh_failure, health_check_failure, etc.


class LogRetriever:
    """
    Retrieves and parses GitHub Actions workflow logs.
    
    This class uses GitHub CLI to fetch workflow logs and parses them
    into a structured format for analysis.
    """
    
    def __init__(self, repo: str, run_id: str):
        """
        Initialize with repository and run ID.
        
        Args:
            repo: GitHub repository in format "owner/repo"
            run_id: GitHub Actions workflow run ID
        """
        self.repo = repo
        self.run_id = run_id
    
    def fetch_logs(self) -> str:
        """
        Fetch raw logs from GitHub using gh CLI.
        
        This method performs the following checks:
        1. Verifies GitHub CLI is installed
        2. Verifies GitHub CLI is authenticated
        3. Fetches workflow logs for the specified run ID
        
        Returns:
            Raw log output as string
            
        Raises:
            RuntimeError: If GitHub CLI is not installed, not authenticated,
                         or if log retrieval fails
        """
        # Check if gh CLI is installed
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            print(f"  GitHub CLI version: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError(
                "GitHub CLI (gh) is not installed.\n"
                "Installation instructions:\n"
                "  - macOS: brew install gh\n"
                "  - Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md\n"
                "  - Windows: See https://github.com/cli/cli#windows\n"
                "  - Or visit: https://cli.github.com/"
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"GitHub CLI (gh) is installed but not working properly.\n"
                f"Error: {e.stderr if e.stderr else 'Unknown error'}"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "GitHub CLI (gh) command timed out. "
                "Please check your installation."
            )
        
        # Check if gh CLI is authenticated
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            print(f"  GitHub CLI authentication: OK")
        except subprocess.CalledProcessError as e:
            # Extract helpful error message from stderr
            error_msg = e.stderr if e.stderr else "Unknown authentication error"
            raise RuntimeError(
                "GitHub CLI is not authenticated.\n"
                "Please authenticate using one of these methods:\n"
                "  1. Interactive login: gh auth login\n"
                "  2. Token authentication: gh auth login --with-token < token.txt\n"
                "  3. Set GITHUB_TOKEN environment variable\n"
                f"\nError details: {error_msg}"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "GitHub CLI authentication check timed out. "
                "Please check your network connection."
            )
        
        # Fetch logs
        print(f"  Fetching logs for run {self.run_id} in {self.repo}...")
        try:
            result = subprocess.run(
                ["gh", "run", "view", self.run_id, "--repo", self.repo, "--log"],
                capture_output=True,
                text=True,
                check=True,
                timeout=60  # Logs can be large, allow more time
            )
            
            if not result.stdout:
                raise RuntimeError(
                    f"No logs returned for run {self.run_id}. "
                    "The workflow run may not exist or may not have started yet."
                )
            
            print(f"  Successfully fetched logs ({len(result.stdout)} bytes)")
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else "Unknown error"
            
            # Provide specific error messages for common issues
            if "not found" in error_msg.lower():
                raise RuntimeError(
                    f"Workflow run {self.run_id} not found in repository {self.repo}.\n"
                    "Please verify:\n"
                    "  1. The run ID is correct\n"
                    "  2. The repository name is in 'owner/repo' format\n"
                    "  3. You have access to this repository\n"
                    f"\nError details: {error_msg}"
                )
            elif "permission" in error_msg.lower() or "forbidden" in error_msg.lower():
                raise RuntimeError(
                    f"Permission denied accessing repository {self.repo}.\n"
                    "Please verify:\n"
                    "  1. You have read access to this repository\n"
                    "  2. Your GitHub token has the required scopes (repo, workflow)\n"
                    f"\nError details: {error_msg}"
                )
            elif "rate limit" in error_msg.lower():
                raise RuntimeError(
                    "GitHub API rate limit exceeded.\n"
                    "Please wait a few minutes and try again, or authenticate with a token.\n"
                    f"\nError details: {error_msg}"
                )
            else:
                raise RuntimeError(
                    f"Failed to fetch logs for run {self.run_id} in {self.repo}.\n"
                    f"Error details: {error_msg}"
                )
                
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"Timeout while fetching logs for run {self.run_id}.\n"
                "The workflow logs may be very large or the network connection is slow.\n"
                "Please try again or check your network connection."
            )
    
    def parse_logs(self, raw_logs: str) -> WorkflowLogs:
        """
        Parse raw logs into structured format.
        
        Args:
            raw_logs: Raw log output from GitHub CLI
            
        Returns:
            WorkflowLogs object with parsed structure
        """
        print("  Parsing workflow logs...")
        
        workflow_logs = WorkflowLogs()
        current_job = None
        current_step = None
        
        # Parse logs line by line
        for line in raw_logs.split('\n'):
            # Job header pattern: "job-name\tTimestamp"
            if '\t' in line and not line.startswith(' '):
                job_name = line.split('\t')[0]
                if job_name and not job_name.startswith(' '):
                    current_job = JobLog(name=job_name, status="unknown")
                    workflow_logs.jobs[job_name] = current_job
                    current_step = None
            
            # Step header pattern: "  step-name\tTimestamp"
            elif line.startswith('  ') and '\t' in line and current_job:
                step_name = line.strip().split('\t')[0]
                if step_name:
                    current_step = StepLog(name=step_name, status="unknown", output="")
                    current_job.steps.append(current_step)
            
            # Step output
            elif current_step and line.startswith('    '):
                current_step.output += line[4:] + '\n'
        
        # Determine overall status
        workflow_logs.overall_status = self._determine_overall_status(workflow_logs)
        workflow_logs.conclusion = self._determine_conclusion(workflow_logs)
        
        return workflow_logs
    
    def _determine_overall_status(self, logs: WorkflowLogs) -> str:
        """Determine overall workflow status from job logs."""
        if not logs.jobs:
            return "unknown"
        
        # Check if any job failed
        for job in logs.jobs.values():
            if "fail" in job.status.lower() or any("error" in step.output.lower() 
                                                    for step in job.steps):
                return "failed"
        
        return "completed"
    
    def _determine_conclusion(self, logs: WorkflowLogs) -> str:
        """Determine workflow conclusion from job logs."""
        status = self._determine_overall_status(logs)
        if status == "failed":
            return "failure"
        elif status == "completed":
            return "success"
        return "unknown"
    
    def identify_failure_point(self, logs: WorkflowLogs) -> Optional[FailurePoint]:
        """
        Identify which job and step failed.
        
        Args:
            logs: Parsed workflow logs
            
        Returns:
            FailurePoint object or None if no failure found
        """
        print("  Identifying failure point...")
        
        for job_name, job in logs.jobs.items():
            for step in job.steps:
                # Look for error indicators in step output
                if self._contains_error(step.output):
                    error_message = self._extract_first_error(step.output)
                    error_type = self._classify_error(step.output)
                    
                    return FailurePoint(
                        job_name=job_name,
                        step_name=step.name,
                        error_message=error_message,
                        error_type=error_type
                    )
        
        return None
    
    def _contains_error(self, output: str) -> bool:
        """Check if output contains error indicators."""
        error_patterns = [
            r'error:',
            r'failed',
            r'exception',
            r'timeout',
            r'connection refused',
            r'command not found',
            r'no such file',
        ]
        
        output_lower = output.lower()
        return any(re.search(pattern, output_lower) for pattern in error_patterns)
    
    def _extract_first_error(self, output: str) -> str:
        """Extract the first error message from output."""
        lines = output.split('\n')
        for line in lines:
            if self._contains_error(line):
                return line.strip()
        return "Unknown error"
    
    def _classify_error(self, output: str) -> str:
        """Classify the type of error based on output."""
        output_lower = output.lower()
        
        if 'ssh' in output_lower and ('timeout' in output_lower or 'connection' in output_lower):
            return "ssh_failure"
        elif 'health' in output_lower or 'endpoint' in output_lower:
            return "health_check_failure"
        elif 'npm' in output_lower or 'node' in output_lower:
            return "dependency_failure"
        elif 'pm2' in output_lower or 'application' in output_lower:
            return "application_startup_failure"
        else:
            return "unknown_failure"
    
    def extract_error_messages(self, logs: WorkflowLogs) -> List[str]:
        """
        Extract all error messages from logs.
        
        Args:
            logs: Parsed workflow logs
            
        Returns:
            List of error messages
        """
        error_messages = []
        
        for job in logs.jobs.values():
            for step in job.steps:
                if self._contains_error(step.output):
                    # Extract all error lines
                    for line in step.output.split('\n'):
                        if self._contains_error(line):
                            error_messages.append(line.strip())
        
        return error_messages
    
    def fetch_and_parse_logs(self) -> WorkflowLogs:
        """
        Convenience method to fetch and parse logs in one call.
        
        Returns:
            WorkflowLogs object with parsed structure
        """
        raw_logs = self.fetch_logs()
        logs = self.parse_logs(raw_logs)
        
        # Identify failure point if workflow failed
        if logs.overall_status == "failed":
            failure_point = self.identify_failure_point(logs)
            if failure_point:
                print(f"  Found failure in job '{failure_point.job_name}', "
                      f"step '{failure_point.step_name}'")
                print(f"  Error type: {failure_point.error_type}")
        
        return logs
