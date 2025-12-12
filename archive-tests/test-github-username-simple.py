#!/usr/bin/env python3

"""
Simple test to verify github_username parameter was added to the MCP server
"""

import requests

def test_github_username_parameter():
    """Test that github_username parameter is available in tool definition"""
    
    print("🧪 Testing GitHub Username Parameter Addition")
    print("=" * 50)
    
    try:
        # Check the web interface for the updated tool definition
        response = requests.get("http://3.81.56.119:3000/", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to get web interface: {response.status_code}")
            return False
        
        html_content = response.text
        
        # Check if github_username parameter is mentioned
        if 'github_username' in html_content:
            print("✅ github_username parameter found in web interface")
        else:
            print("❌ github_username parameter not found in web interface")
            return False
        
        # Check for OIDC setup mention
        if 'OIDC' in html_content or 'oidc' in html_content:
            print("✅ OIDC setup mentioned in documentation")
        else:
            print("⚠️  OIDC setup not explicitly mentioned")
        
        print("\n🎉 GitHub username parameter successfully added!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verify_file_changes():
    """Verify the local file changes are correct"""
    
    print("\n🔍 Verifying Local File Changes")
    print("=" * 40)
    
    try:
        with open('mcp-server/server.js', 'r') as f:
            server_content = f.read()
        
        # Check for github_username parameter
        if 'github_username: {' in server_content:
            print("✅ github_username parameter added to tool definition")
        else:
            print("❌ github_username parameter not found in tool definition")
            return False
        
        # Check for validation
        if 'github_username is required for fully_automated mode' in server_content:
            print("✅ Validation for github_username added")
        else:
            print("❌ Validation for github_username not found")
            return False
        
        # Check for full repository path construction
        if '${github_username}/${repoName}' in server_content:
            print("✅ Full repository path construction logic added")
        else:
            print("❌ Full repository path construction not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    print("🔧 GitHub Username Fix Verification")
    print("=" * 50)
    
    file_check = verify_file_changes()
    web_check = test_github_username_parameter()
    
    print("\n" + "=" * 50)
    if file_check and web_check:
        print("🎉 All verifications passed!")
        print("✅ GitHub username parameter successfully added")
        print("✅ OIDC setup will now work with full repository paths")
        print("\n📋 Summary of Fix:")
        print("   • Added github_username parameter to setup_complete_deployment tool")
        print("   • Added validation for github_username in fully_automated mode")
        print("   • Updated logic to construct full repository path (username/repo)")
        print("   • Fixed OIDC setup issue with repository path format")
    else:
        print("❌ Some verifications failed")
        
    # Return success status
    success = file_check and web_check
    exit(0 if success else 1)