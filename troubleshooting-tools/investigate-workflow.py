#!/usr/bin/env python3
"""
Main entry point for the Lightsail Deployment Workflow Investigation Tool.

This tool investigates GitHub Actions workflow failures for AWS Lightsail deployments,
diagnoses issues, and applies automated fixes.

Usage:
    python investigate-workflow.py --repo OWNER/REPO --run-id RUN_ID [--region REGION] [--apply-fixes]

Example:
    python investigate-workflow.py --repo naveenraj44125-creator/test-deployment-1770711871 --run-id 21857245881
"""

import argparse
import sys
from typing import Optional
from dataclasses import dataclass

from log_retriever import LogRetriever, WorkflowLogs
from diagnostic_engine import DiagnosticEngine, Diagnosis
from fix_applier import FixApplier, FixReport


@dataclass
class DiagnosticReport:
    """Comprehensive diagnostic report containing all investigation results."""
    workflow_logs: WorkflowLogs
    diagnosis: Diagnosis
    fix_report: Optional[FixReport]
    success: bool
    summary: str


class WorkflowInvestigator:
    """
    Main orchestrator for workflow investigation, diagnosis, and fix application.
    
    This class coordinates the three-phase investigation process:
    1. Investigation Phase: Retrieve workflow logs and identify failure point
    2. Diagnosis Phase: Run diagnostic scripts to understand root cause
    3. Fix Phase: Apply automated fixes and verify deployment
    """
    
    def __init__(self, repo: str, run_id: str, region: str = "us-east-1"):
        """
        Initialize the investigator with repository and run ID.
        
        Args:
            repo: GitHub repository in format "owner/repo"
            run_id: GitHub Actions workflow run ID
            region: AWS region for Lightsail instance (default: us-east-1)
        """
        self.repo = repo
        self.run_id = run_id
        self.region = region
        
        # Initialize component classes
        self.log_retriever = LogRetriever(repo, run_id)
        self.diagnostic_engine = None  # Will be initialized after we get instance name
        self.fix_applier = None  # Will be initialized if fixes are needed
    
    def investigate(self) -> DiagnosticReport:
        """
        Run full investigation and return comprehensive report.
        
        Returns:
            DiagnosticReport containing all investigation results
        """
        print(f"Starting investigation of workflow run {self.run_id} in {self.repo}")
        print("=" * 80)
        
        # Phase 1: Retrieve logs
        print("\n[Phase 1] Retrieving workflow logs...")
        logs = self.retrieve_logs()
        
        # Phase 2: Diagnose
        print("\n[Phase 2] Diagnosing failure...")
        diagnosis = self.diagnose(logs)
        
        # Phase 3: Apply fixes (if requested)
        fix_report = None
        
        # Generate report
        report = DiagnosticReport(
            workflow_logs=logs,
            diagnosis=diagnosis,
            fix_report=fix_report,
            success=diagnosis is not None,
            summary=self.generate_report(logs, diagnosis, fix_report)
        )
        
        return report
    
    def retrieve_logs(self) -> WorkflowLogs:
        """
        Retrieve workflow logs from GitHub.
        
        Returns:
            WorkflowLogs object containing parsed logs
        """
        return self.log_retriever.fetch_and_parse_logs()
    
    def diagnose(self, logs: WorkflowLogs) -> Diagnosis:
        """
        Diagnose the failure based on logs and instance state.
        
        Args:
            logs: Parsed workflow logs
            
        Returns:
            Diagnosis object with root cause and recommended fixes
        """
        # Extract instance name from logs (will be implemented in diagnostic_engine)
        # For now, return a placeholder
        print("  Diagnosis functionality will be implemented in Task 3")
        return None
    
    def apply_fixes(self, diagnosis: Diagnosis) -> FixReport:
        """
        Apply automated fixes based on diagnosis.
        
        Args:
            diagnosis: Diagnosis object with recommended fixes
            
        Returns:
            FixReport object with results of fix application
        """
        print("  Fix application functionality will be implemented in Task 5")
        return None
    
    def generate_report(self, logs: WorkflowLogs, diagnosis: Optional[Diagnosis], 
                       fix_report: Optional[FixReport]) -> str:
        """
        Generate human-readable diagnostic report.
        
        Args:
            logs: Workflow logs
            diagnosis: Diagnosis results
            fix_report: Fix application results
            
        Returns:
            Formatted report string
        """
        report_lines = []
        report_lines.append("\n" + "=" * 80)
        report_lines.append("DIAGNOSTIC REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"\nRepository: {self.repo}")
        report_lines.append(f"Run ID: {self.run_id}")
        report_lines.append(f"Region: {self.region}")
        
        # Workflow status section
        report_lines.append("\n" + "-" * 80)
        report_lines.append("WORKFLOW STATUS")
        report_lines.append("-" * 80)
        if logs:
            report_lines.append(f"Overall Status: {logs.overall_status}")
            report_lines.append(f"Conclusion: {logs.conclusion}")
        else:
            report_lines.append("Unable to retrieve workflow logs")
        
        # Diagnosis section
        if diagnosis:
            report_lines.append("\n" + "-" * 80)
            report_lines.append("DIAGNOSIS")
            report_lines.append("-" * 80)
            report_lines.append(f"Failure Type: {diagnosis.failure_type}")
            report_lines.append(f"Root Cause: {diagnosis.root_cause}")
            report_lines.append(f"Confidence: {diagnosis.confidence:.0%}")
            report_lines.append("\nRecommended Fixes:")
            for i, fix in enumerate(diagnosis.recommended_fixes, 1):
                report_lines.append(f"  {i}. {fix}")
        
        # Fix report section
        if fix_report:
            report_lines.append("\n" + "-" * 80)
            report_lines.append("FIXES APPLIED")
            report_lines.append("-" * 80)
            report_lines.append(f"Success: {fix_report.success}")
            if fix_report.fixes_applied:
                report_lines.append("\nSuccessfully Applied:")
                for fix in fix_report.fixes_applied:
                    report_lines.append(f"  ✓ {fix}")
            if fix_report.fixes_failed:
                report_lines.append("\nFailed:")
                for fix in fix_report.fixes_failed:
                    report_lines.append(f"  ✗ {fix}")
        
        report_lines.append("\n" + "=" * 80)
        
        return "\n".join(report_lines)


def main():
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Investigate GitHub Actions workflow failures for AWS Lightsail deployments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Investigate a workflow failure
  python investigate-workflow.py --repo owner/repo --run-id 12345678

  # Investigate and apply fixes
  python investigate-workflow.py --repo owner/repo --run-id 12345678 --apply-fixes

  # Specify AWS region
  python investigate-workflow.py --repo owner/repo --run-id 12345678 --region us-west-2
        """
    )
    
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository in format 'owner/repo'"
    )
    
    parser.add_argument(
        "--run-id",
        required=True,
        help="GitHub Actions workflow run ID"
    )
    
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region for Lightsail instance (default: us-east-1)"
    )
    
    parser.add_argument(
        "--apply-fixes",
        action="store_true",
        help="Automatically apply recommended fixes"
    )
    
    args = parser.parse_args()
    
    try:
        # Create investigator and run investigation
        investigator = WorkflowInvestigator(args.repo, args.run_id, args.region)
        report = investigator.investigate()
        
        # Print report
        print(report.summary)
        
        # Exit with appropriate code
        sys.exit(0 if report.success else 1)
        
    except KeyboardInterrupt:
        print("\n\nInvestigation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nERROR: Investigation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
