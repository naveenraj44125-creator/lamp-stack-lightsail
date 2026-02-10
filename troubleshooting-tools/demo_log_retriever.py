#!/usr/bin/env python3
"""
Demonstration script for LogRetriever GitHub CLI integration.

This script demonstrates the enhanced error handling and GitHub CLI integration
implemented in Task 2.1.
"""

from log_retriever import LogRetriever


def demo_error_handling():
    """Demonstrate various error handling scenarios."""
    
    print("=" * 70)
    print("LogRetriever GitHub CLI Integration Demo")
    print("=" * 70)
    print()
    
    # Example 1: Create a LogRetriever instance
    print("1. Creating LogRetriever instance...")
    retriever = LogRetriever(
        repo="naveenraj44125-creator/test-deployment-1770711871",
        run_id="21857245881"
    )
    print(f"   Repository: {retriever.repo}")
    print(f"   Run ID: {retriever.run_id}")
    print()
    
    # Example 2: Demonstrate error handling
    print("2. Error Handling Features:")
    print("   ✓ Checks if GitHub CLI is installed")
    print("   ✓ Verifies GitHub CLI is authenticated")
    print("   ✓ Provides detailed error messages for:")
    print("     - CLI not installed (with installation instructions)")
    print("     - CLI not authenticated (with authentication commands)")
    print("     - Run not found (with verification steps)")
    print("     - Permission denied (with access requirements)")
    print("     - Rate limit exceeded (with retry guidance)")
    print("     - Timeout errors (with troubleshooting tips)")
    print("     - Empty log responses")
    print()
    
    # Example 3: Show what happens when fetching logs
    print("3. Attempting to fetch logs...")
    print("   (This will check GitHub CLI installation and authentication)")
    print()
    
    try:
        logs = retriever.fetch_logs()
        print("   ✓ Successfully fetched logs!")
        print(f"   Log size: {len(logs)} bytes")
        print()
        
        # Parse and analyze
        print("4. Parsing logs...")
        parsed_logs = retriever.parse_logs(logs)
        print(f"   Found {len(parsed_logs.jobs)} jobs")
        print(f"   Overall status: {parsed_logs.overall_status}")
        print(f"   Conclusion: {parsed_logs.conclusion}")
        print()
        
        # Identify failures
        if parsed_logs.overall_status == "failed":
            print("5. Identifying failure point...")
            failure = retriever.identify_failure_point(parsed_logs)
            if failure:
                print(f"   Job: {failure.job_name}")
                print(f"   Step: {failure.step_name}")
                print(f"   Error type: {failure.error_type}")
                print(f"   Error message: {failure.error_message[:100]}...")
        
    except RuntimeError as e:
        print("   ✗ Error occurred (this is expected if GitHub CLI is not set up):")
        print()
        print(str(e))
        print()
        print("   This demonstrates the enhanced error handling!")
    
    print()
    print("=" * 70)
    print("Demo Complete")
    print("=" * 70)


if __name__ == "__main__":
    demo_error_handling()
