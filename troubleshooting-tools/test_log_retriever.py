"""
Unit tests for LogRetriever module.

Tests the GitHub CLI integration, error handling, and log parsing functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess
from log_retriever import LogRetriever, WorkflowLogs, JobLog, StepLog, FailurePoint


class TestLogRetrieverGitHubCLI(unittest.TestCase):
    """Test GitHub CLI integration and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.retriever = LogRetriever("owner/repo", "12345")
    
    @patch('subprocess.run')
    def test_fetch_logs_success(self, mock_run):
        """Test successful log retrieval."""
        # Mock gh --version
        mock_run.side_effect = [
            MagicMock(stdout="gh version 2.0.0", returncode=0),  # gh --version
            MagicMock(stdout="Logged in", returncode=0),  # gh auth status
            MagicMock(stdout="job1\t2024-01-01\n  step1\t2024-01-01\n    output", returncode=0)  # gh run view
        ]
        
        result = self.retriever.fetch_logs()
        
        self.assertIsInstance(result, str)
        self.assertIn("job1", result)
        self.assertEqual(mock_run.call_count, 3)
    
    @patch('subprocess.run')
    def test_fetch_logs_gh_not_installed(self, mock_run):
        """Test error when GitHub CLI is not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        with self.assertRaises(RuntimeError) as context:
            self.retriever.fetch_logs()
        
        self.assertIn("not installed", str(context.exception))
        self.assertIn("https://cli.github.com", str(context.exception))
    
    @patch('subprocess.run')
    def test_fetch_logs_gh_not_working(self, mock_run):
        """Test error when GitHub CLI is not working properly."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["gh", "--version"], stderr="Command failed"
        )
        
        with self.assertRaises(RuntimeError) as context:
            self.retriever.fetch_logs()
        
        self.assertIn("not working properly", str(context.exception))
    
    @patch('subprocess.run')
    def test_fetch_logs_gh_not_authenticated(self, mock_run):
        """Test error when GitHub CLI is not authenticated."""
        mock_run.side_effect = [
            MagicMock(stdout="gh version 2.0.0", returncode=0),  # gh --version
            subprocess.CalledProcessError(1, ["gh", "auth", "status"], stderr="Not logged in")
        ]
        
        with self.assertRaises(RuntimeError) as context:
            self.retriever.fetch_logs()
        
        self.assertIn("not authenticated", str(context.exception))
        self.assertIn("gh auth login", str(context.exception))
    
    @patch('subprocess.run')
    def test_fetch_logs_run_not_found(self, mock_run):
        """Test error when workflow run is not found."""
        mock_run.side_effect = [
            MagicMock(stdout="gh version 2.0.0", returncode=0),  # gh --version
            MagicMock(stdout="Logged in", returncode=0),  # gh auth status
            subprocess.CalledProcessError(1, ["gh", "run", "view"], stderr="run not found")
        ]
        
        with self.assertRaises(RuntimeError) as context:
            self.retriever.fetch_logs()
        
        self.assertIn("not found", str(context.exception))
        self.assertIn("run ID is correct", str(context.exception))
    
    @patch('subprocess.run')
    def test_fetch_logs_permission_denied(self, mock_run):
        """Test error when permission is denied."""
        mock_run.side_effect = [
            MagicMock(stdout="gh version 2.0.0", returncode=0),  # gh --version
            MagicMock(stdout="Logged in", returncode=0),  # gh auth status
            subprocess.CalledProcessError(1, ["gh", "run", "view"], stderr="permission denied")
        ]
        
        with self.assertRaises(RuntimeError) as context:
            self.retriever.fetch_logs()
        
        self.assertIn("Permission denied", str(context.exception))
        self.assertIn("read access", str(context.exception))
    
    @patch('subprocess.run')
    def test_fetch_logs_rate_limit(self, mock_run):
        """Test error when rate limit is exceeded."""
        mock_run.side_effect = [
            MagicMock(stdout="gh version 2.0.0", returncode=0),  # gh --version
            MagicMock(stdout="Logged in", returncode=0),  # gh auth status
            subprocess.CalledProcessError(1, ["gh", "run", "view"], stderr="rate limit exceeded")
        ]
        
        with self.assertRaises(RuntimeError) as context:
            self.retriever.fetch_logs()
        
        self.assertIn("rate limit", str(context.exception))
    
    @patch('subprocess.run')
    def test_fetch_logs_timeout(self, mock_run):
        """Test error when command times out."""
        mock_run.side_effect = [
            MagicMock(stdout="gh version 2.0.0", returncode=0),  # gh --version
            MagicMock(stdout="Logged in", returncode=0),  # gh auth status
            subprocess.TimeoutExpired(["gh", "run", "view"], 60)
        ]
        
        with self.assertRaises(RuntimeError) as context:
            self.retriever.fetch_logs()
        
        self.assertIn("Timeout", str(context.exception))
    
    @patch('subprocess.run')
    def test_fetch_logs_empty_response(self, mock_run):
        """Test error when no logs are returned."""
        mock_run.side_effect = [
            MagicMock(stdout="gh version 2.0.0", returncode=0),  # gh --version
            MagicMock(stdout="Logged in", returncode=0),  # gh auth status
            MagicMock(stdout="", returncode=0)  # Empty logs
        ]
        
        with self.assertRaises(RuntimeError) as context:
            self.retriever.fetch_logs()
        
        self.assertIn("No logs returned", str(context.exception))


class TestLogRetrieverParsing(unittest.TestCase):
    """Test log parsing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.retriever = LogRetriever("owner/repo", "12345")
    
    def test_parse_logs_simple(self):
        """Test parsing simple workflow logs."""
        raw_logs = """job1\t2024-01-01T00:00:00Z
  step1\t2024-01-01T00:00:01Z
    Step output line 1
    Step output line 2
  step2\t2024-01-01T00:00:02Z
    Step 2 output
job2\t2024-01-01T00:00:03Z
  step3\t2024-01-01T00:00:04Z
    Step 3 output"""
        
        logs = self.retriever.parse_logs(raw_logs)
        
        self.assertIsInstance(logs, WorkflowLogs)
        self.assertEqual(len(logs.jobs), 2)
        self.assertIn("job1", logs.jobs)
        self.assertIn("job2", logs.jobs)
        self.assertEqual(len(logs.jobs["job1"].steps), 2)
        self.assertEqual(logs.jobs["job1"].steps[0].name, "step1")
        self.assertIn("Step output line 1", logs.jobs["job1"].steps[0].output)
    
    def test_parse_logs_with_errors(self):
        """Test parsing logs with error messages."""
        raw_logs = """job1\t2024-01-01T00:00:00Z
  step1\t2024-01-01T00:00:01Z
    Error: Connection timeout
    Failed to connect"""
        
        logs = self.retriever.parse_logs(raw_logs)
        
        self.assertEqual(logs.overall_status, "failed")
        self.assertEqual(logs.conclusion, "failure")
    
    def test_parse_logs_empty(self):
        """Test parsing empty logs."""
        logs = self.retriever.parse_logs("")
        
        self.assertIsInstance(logs, WorkflowLogs)
        self.assertEqual(len(logs.jobs), 0)
        self.assertEqual(logs.overall_status, "unknown")


class TestLogRetrieverFailureIdentification(unittest.TestCase):
    """Test failure point identification."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.retriever = LogRetriever("owner/repo", "12345")
    
    def test_identify_ssh_failure(self):
        """Test identification of SSH connection failure."""
        raw_logs = """job1\t2024-01-01T00:00:00Z
  step1\t2024-01-01T00:00:01Z
    SSH connection timeout
    Failed to connect to host"""
        
        logs = self.retriever.parse_logs(raw_logs)
        failure = self.retriever.identify_failure_point(logs)
        
        self.assertIsNotNone(failure)
        self.assertEqual(failure.job_name, "job1")
        self.assertEqual(failure.step_name, "step1")
        self.assertEqual(failure.error_type, "ssh_failure")
        self.assertIn("SSH", failure.error_message)
    
    def test_identify_health_check_failure(self):
        """Test identification of health check failure."""
        raw_logs = """verification\t2024-01-01T00:00:00Z
  health-check\t2024-01-01T00:00:01Z
    Health endpoint returned 500
    Error: Service unavailable"""
        
        logs = self.retriever.parse_logs(raw_logs)
        failure = self.retriever.identify_failure_point(logs)
        
        self.assertIsNotNone(failure)
        self.assertEqual(failure.error_type, "health_check_failure")
    
    def test_identify_npm_failure(self):
        """Test identification of npm/dependency failure."""
        raw_logs = """build\t2024-01-01T00:00:00Z
  install\t2024-01-01T00:00:01Z
    npm ERR! code ENOENT
    npm ERR! Failed to install dependencies"""
        
        logs = self.retriever.parse_logs(raw_logs)
        failure = self.retriever.identify_failure_point(logs)
        
        self.assertIsNotNone(failure)
        self.assertEqual(failure.error_type, "dependency_failure")
    
    def test_identify_no_failure(self):
        """Test when no failure is present."""
        raw_logs = """job1\t2024-01-01T00:00:00Z
  step1\t2024-01-01T00:00:01Z
    Success: All tests passed"""
        
        logs = self.retriever.parse_logs(raw_logs)
        failure = self.retriever.identify_failure_point(logs)
        
        self.assertIsNone(failure)


class TestLogRetrieverErrorExtraction(unittest.TestCase):
    """Test error message extraction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.retriever = LogRetriever("owner/repo", "12345")
    
    def test_extract_multiple_errors(self):
        """Test extraction of multiple error messages."""
        raw_logs = """job1\t2024-01-01T00:00:00Z
  step1\t2024-01-01T00:00:01Z
    Error: First error
    Warning: This is a warning
    Error: Second error
  step2\t2024-01-01T00:00:02Z
    Failed: Third error"""
        
        logs = self.retriever.parse_logs(raw_logs)
        errors = self.retriever.extract_error_messages(logs)
        
        self.assertGreater(len(errors), 0)
        # Should extract error lines
        error_text = " ".join(errors)
        self.assertIn("Error", error_text)
    
    def test_extract_no_errors(self):
        """Test extraction when no errors are present."""
        raw_logs = """job1\t2024-01-01T00:00:00Z
  step1\t2024-01-01T00:00:01Z
    Success: Everything is fine"""
        
        logs = self.retriever.parse_logs(raw_logs)
        errors = self.retriever.extract_error_messages(logs)
        
        self.assertEqual(len(errors), 0)


class TestLogRetrieverIntegration(unittest.TestCase):
    """Integration tests for complete workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.retriever = LogRetriever("owner/repo", "12345")
    
    @patch('subprocess.run')
    def test_fetch_and_parse_logs_success(self, mock_run):
        """Test complete fetch and parse workflow."""
        mock_run.side_effect = [
            MagicMock(stdout="gh version 2.0.0", returncode=0),
            MagicMock(stdout="Logged in", returncode=0),
            MagicMock(stdout="job1\t2024-01-01\n  step1\t2024-01-01\n    output", returncode=0)
        ]
        
        logs = self.retriever.fetch_and_parse_logs()
        
        self.assertIsInstance(logs, WorkflowLogs)
        self.assertGreater(len(logs.jobs), 0)
    
    @patch('subprocess.run')
    def test_fetch_and_parse_logs_with_failure(self, mock_run):
        """Test complete workflow with failure detection."""
        mock_run.side_effect = [
            MagicMock(stdout="gh version 2.0.0", returncode=0),
            MagicMock(stdout="Logged in", returncode=0),
            MagicMock(stdout="job1\t2024-01-01\n  step1\t2024-01-01\n    Error: Failed", returncode=0)
        ]
        
        logs = self.retriever.fetch_and_parse_logs()
        
        self.assertEqual(logs.overall_status, "failed")


if __name__ == '__main__':
    unittest.main()
