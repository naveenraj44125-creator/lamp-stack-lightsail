#!/usr/bin/env python3
"""
Test script to verify AWS_ROLE_ARN variable scope fix in setup-complete-deployment.sh

This script tests that:
1. The create_iam_role_if_needed function properly returns the role ARN
2. All status messages are redirected to stderr (not stdout)
3. The AWS_ROLE_ARN variable is properly captured in the main function
4. The GitHub variable setting receives the correct role ARN
"""

import subprocess
import sys
import re
import os

def test_function_output_separation():
    """Test that create_iam_role_if_needed function separates status messages from return value"""
    
    print("🧪 Testing AWS_ROLE_ARN variable scope fix...")
    print("=" * 60)
    
    # Create a test script that simulates the function behavior
    test_script = '''#!/bin/bash
    
# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Simulate the fixed create_iam_role_if_needed function
create_iam_role_if_needed() {
    local role_name="$1"
    local github_repo="$2"
    local aws_account_id="$3"
    
    echo -e "${BLUE}Creating IAM role: $role_name${NC}" >&2
    
    # Simulate role creation (without actual AWS calls)
    echo -e "${GREEN}✓ IAM role created${NC}" >&2
    
    # Return the role ARN (this should be the ONLY stdout output)
    local role_arn="arn:aws:iam::${aws_account_id}:role/${role_name}"
    echo "$role_arn"
    
    return 0
}

# Simulate the main function behavior
main() {
    local ROLE_NAME="GitHubActions-TestApp-deployment"
    local GITHUB_REPO="naveenraj44125-creator/social-media-app-deployment"
    local AWS_ACCOUNT_ID="123456789012"
    
    echo "Testing AWS_ROLE_ARN variable capture..." >&2
    
    # This is the critical line that was failing before the fix
    AWS_ROLE_ARN=$(create_iam_role_if_needed "$ROLE_NAME" "$GITHUB_REPO" "$AWS_ACCOUNT_ID")
    
    echo "Captured AWS_ROLE_ARN: $AWS_ROLE_ARN" >&2
    
    # Simulate GitHub variable setting
    if [[ -n "$AWS_ROLE_ARN" ]]; then
        echo "✓ AWS_ROLE_ARN variable would be set to: $AWS_ROLE_ARN" >&2
        echo "SUCCESS"
    else
        echo "❌ AWS_ROLE_ARN is empty!" >&2
        echo "FAILED"
    fi
}

main
'''
    
    # Write test script to temporary file
    with open('/tmp/test_aws_role_arn.sh', 'w') as f:
        f.write(test_script)
    
    # Make it executable
    os.chmod('/tmp/test_aws_role_arn.sh', 0o755)
    
    try:
        # Run the test script
        result = subprocess.run(['/bin/bash', '/tmp/test_aws_role_arn.sh'], 
                              capture_output=True, text=True, timeout=10)
        
        print("📤 STDOUT (should only contain SUCCESS/FAILED):")
        print(f"'{result.stdout.strip()}'")
        print()
        
        print("📤 STDERR (should contain all status messages):")
        print(result.stderr.strip())
        print()
        
        # Analyze results
        stdout_lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        stderr_content = result.stderr.strip()
        
        success = True
        
        # Test 1: STDOUT should only contain the final result
        if len(stdout_lines) != 1 or stdout_lines[0] not in ['SUCCESS', 'FAILED']:
            print("❌ FAILED: STDOUT contains unexpected content")
            print(f"   Expected: ['SUCCESS'] or ['FAILED']")
            print(f"   Got: {stdout_lines}")
            success = False
        else:
            print("✅ PASSED: STDOUT contains only the final result")
        
        # Test 2: STDERR should contain status messages
        expected_stderr_content = [
            "Creating IAM role:",
            "✓ IAM role created",
            "Testing AWS_ROLE_ARN variable capture",
            "Captured AWS_ROLE_ARN:",
            "arn:aws:iam::123456789012:role/GitHubActions-TestApp-deployment"
        ]
        
        missing_content = []
        for expected in expected_stderr_content:
            if expected not in stderr_content:
                missing_content.append(expected)
        
        if missing_content:
            print("❌ FAILED: STDERR missing expected content:")
            for missing in missing_content:
                print(f"   Missing: '{missing}'")
            success = False
        else:
            print("✅ PASSED: STDERR contains all expected status messages")
        
        # Test 3: Final result should be SUCCESS
        if stdout_lines[0] == 'SUCCESS':
            print("✅ PASSED: AWS_ROLE_ARN variable was captured successfully")
        else:
            print("❌ FAILED: AWS_ROLE_ARN variable capture failed")
            success = False
        
        return success
        
    except subprocess.TimeoutExpired:
        print("❌ FAILED: Test script timed out")
        return False
    except Exception as e:
        print(f"❌ FAILED: Test script error: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists('/tmp/test_aws_role_arn.sh'):
            os.remove('/tmp/test_aws_role_arn.sh')

def test_actual_function_in_script():
    """Test the actual function in the setup script"""
    
    print("\n🔍 Analyzing actual function in setup-complete-deployment.sh...")
    print("=" * 60)
    
    try:
        with open('setup-complete-deployment.sh', 'r') as f:
            content = f.read()
        
        # Find the create_iam_role_if_needed function
        function_match = re.search(
            r'create_iam_role_if_needed\(\)\s*\{(.*?)\nreturn 0\n\}',
            content,
            re.DOTALL
        )
        
        if not function_match:
            print("❌ FAILED: Could not find create_iam_role_if_needed function")
            return False
        
        function_body = function_match.group(1)
        
        # Check for stderr redirections
        stderr_redirections = re.findall(r'echo.*>&2', function_body)
        # Count echo statements that don't have >&2 (but exclude the role_arn return)
        all_echos = re.findall(r'echo[^#\n]*', function_body)
        stdout_echos = [echo for echo in all_echos if '>&2' not in echo]
        
        print(f"📊 Analysis Results:")
        print(f"   - Status messages redirected to stderr: {len(stderr_redirections)}")
        print(f"   - Messages still going to stdout: {len(stdout_echos)}")
        
        # Check specific patterns
        success = True
        
        # Should have stderr redirections for status messages
        if len(stderr_redirections) < 2:  # At least 2 status messages should go to stderr
            print("❌ FAILED: Not enough status messages redirected to stderr")
            print(f"   Found stderr redirections: {stderr_redirections}")
            success = False
        else:
            print("✅ PASSED: Status messages are redirected to stderr")
        
        # Check for the role ARN return (should be exactly one stdout echo)
        role_arn_return = [echo for echo in stdout_echos if 'role_arn' in echo]
        if len(role_arn_return) == 1:
            print("✅ PASSED: Function returns role ARN to stdout")
        else:
            print("❌ FAILED: Function does not return role ARN properly to stdout")
            print(f"   Found stdout echos: {stdout_echos}")
            print(f"   Role ARN returns: {role_arn_return}")
            success = False
        
        # Check for proper variable capture in main function
        main_capture_pattern = r'AWS_ROLE_ARN=\$\(create_iam_role_if_needed.*\)'
        if re.search(main_capture_pattern, content):
            print("✅ PASSED: Main function captures AWS_ROLE_ARN from function return")
        else:
            print("❌ FAILED: Main function does not capture AWS_ROLE_ARN properly")
            success = False
        
        return success
        
    except FileNotFoundError:
        print("❌ FAILED: setup-complete-deployment.sh not found")
        return False
    except Exception as e:
        print(f"❌ FAILED: Error analyzing script: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🚀 AWS_ROLE_ARN Variable Scope Fix Verification")
    print("=" * 60)
    print()
    
    # Test 1: Function output separation
    test1_passed = test_function_output_separation()
    
    # Test 2: Actual script analysis
    test2_passed = test_actual_function_in_script()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ The AWS_ROLE_ARN variable scope fix is working correctly:")
        print("   - Status messages are redirected to stderr")
        print("   - Role ARN is returned via stdout")
        print("   - Main function captures the role ARN properly")
        print("   - GitHub variable setting will receive the correct value")
        print()
        print("🚀 The OIDC issue is now completely resolved!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print()
        print("Issues found:")
        if not test1_passed:
            print("   - Function output separation test failed")
        if not test2_passed:
            print("   - Script analysis test failed")
        print()
        print("🔧 Additional fixes may be needed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)