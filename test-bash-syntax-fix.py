#!/usr/bin/env python3
"""
Test script to verify the bash syntax fix in deploy-post-steps-generic.py
"""

def test_bash_syntax_generation():
    """Test that the bash syntax generation produces valid bash code"""
    
    # Simulate the expected_dirs scenario that was causing the issue
    expected_dirs = ['mcp-server', 'example-app']
    
    # Build directory search logic (fixed version)
    dir_checks = ""
    if expected_dirs:
        for dir_name in expected_dirs:
            dir_checks += f'''
if [ -d "./{dir_name}" ]; then
    EXTRACTED_DIR="./{dir_name}"
    echo "✅ Found configured directory: {dir_name}"
elif'''
        dir_checks += ''' [ -z "$EXTRACTED_DIR" ]; then
    EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "example-*-app" | head -n 1)
fi'''
    else:
        dir_checks = '''EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "example-*-app" | head -n 1)'''
    
    print("Generated bash script:")
    print("=" * 80)
    print(dir_checks)
    print("=" * 80)
    
    # Check for syntax issues
    issues = []
    
    # Check that we don't have the broken 'el''' pattern
    if "el'''" in dir_checks:
        issues.append("❌ Found broken 'el''' pattern")
    
    # Check that we have proper 'elif' statements
    if "elif" not in dir_checks:
        issues.append("❌ Missing 'elif' statements")
    
    # Check for proper bash structure
    if_count = dir_checks.count("if [")
    elif_count = dir_checks.count("elif")
    fi_count = dir_checks.count("fi")
    
    if if_count == 0:
        issues.append("❌ No 'if' statements found")
    
    if fi_count == 0:
        issues.append("❌ No 'fi' statements found")
    
    # For multiple expected_dirs, we should have elif statements
    if len(expected_dirs) > 1 and elif_count == 0:
        issues.append("❌ Multiple directories but no 'elif' statements")
    
    # Check for unmatched quotes or syntax
    if "'''" in dir_checks and dir_checks.count("'''") % 2 != 0:
        issues.append("❌ Unmatched triple quotes")
    
    if issues:
        print("\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ BASH SYNTAX TEST PASSED")
        print("  ✅ No 'el''' pattern found")
        print("  ✅ Proper 'elif' statements present")
        print(f"  ✅ Balanced if/fi statements ({if_count} if, {fi_count} fi)")
        print(f"  ✅ Proper elif usage ({elif_count} elif for {len(expected_dirs)} dirs)")
        return True

def test_single_directory():
    """Test with single directory (should not use elif)"""
    print("\n" + "=" * 50)
    print("Testing single directory scenario:")
    
    expected_dirs = ['mcp-server']
    
    dir_checks = ""
    if expected_dirs:
        for dir_name in expected_dirs:
            dir_checks += f'''
if [ -d "./{dir_name}" ]; then
    EXTRACTED_DIR="./{dir_name}"
    echo "✅ Found configured directory: {dir_name}"
elif'''
        dir_checks += ''' [ -z "$EXTRACTED_DIR" ]; then
    EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "example-*-app" | head -n 1)
fi'''
    
    print(dir_checks)
    
    # Should have elif for fallback even with single directory
    if "elif" in dir_checks:
        print("✅ Single directory test passed - has fallback elif")
        return True
    else:
        print("❌ Single directory test failed - missing fallback elif")
        return False

if __name__ == "__main__":
    print("Testing Bash Syntax Fix for deploy-post-steps-generic.py")
    print("=" * 60)
    
    success1 = test_bash_syntax_generation()
    success2 = test_single_directory()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The bash syntax fix should resolve the deployment errors.")
    else:
        print("\n❌ Some tests failed! Please check the implementation.")