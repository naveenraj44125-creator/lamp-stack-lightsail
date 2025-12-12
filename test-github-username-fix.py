#!/usr/bin/env python3

"""
Test script to verify the MCP server correctly handles github_username parameter
and constructs full repository paths for OIDC setup
"""

import json
import requests
import sys

def test_github_username_fix():
    """Test that MCP server correctly handles github_username parameter"""
    
    print("🧪 Testing GitHub Username Fix for OIDC Setup")
    print("=" * 60)
    
    # MCP server URL
    mcp_url = "http://3.81.56.119:3000"
    
    try:
        # Test 1: Call setup_complete_deployment with github_username
        print("\n🚀 Test 1: Testing fully_automated mode with github_username...")
        
        setup_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": {
                    "mode": "fully_automated",
                    "app_type": "nodejs",
                    "app_name": "social-media-app-deployment",
                    "github_username": "naveenraj44125-creator",
                    "github_repo": "social-media-app-deployment",
                    "aws_region": "us-east-1",
                    "bundle_id": "small_3_0",
                    "database_type": "postgresql",
                    "db_external": True,
                    "enable_bucket": True,
                    "repo_visibility": "public"
                }
            }
        }
        
        # Try different endpoints to find the working one
        endpoints = ["/sse", "/message", "/api"]
        response = None
        
        for endpoint in endpoints:
            try:
                response = requests.post(f"{mcp_url}{endpoint}", json=setup_payload, timeout=30)
                if response.status_code == 200:
                    break
            except:
                continue
        
        if not response or response.status_code != 200:
            print(f"❌ Failed to call setup_complete_deployment on any endpoint")
            return False
        
        result_data = response.json()
        
        if 'error' in result_data:
            print(f"❌ MCP call failed: {result_data['error']}")
            return False
        
        # Check the response content for correct GitHub repository format
        content = result_data.get('result', {}).get('content', [])
        if not content:
            print("❌ No content in response")
            return False
        
        response_text = content[0].get('text', '')
        
        # Test 1: Check environment variables show full repository path
        if 'export GITHUB_REPO="naveenraj44125-creator/social-media-app-deployment"' in response_text:
            print("✅ Environment variables correctly show full repository path")
        elif 'export GITHUB_REPO="social-media-app-deployment"' in response_text:
            print("❌ Environment variables still show only repository name")
            return False
        else:
            print("⚠️  GITHUB_REPO environment variable not found in response")
            print(f"Response preview: {response_text[:1000]}...")
        
        # Test 2: Check configuration summary shows full repository
        if 'naveenraj44125-creator/social-media-app-deployment' in response_text:
            print("✅ Configuration summary shows full repository path")
        else:
            print("❌ Configuration summary doesn't show full repository path")
            return False
        
        # Test 3: Check GitHub username is displayed
        if 'Username**: naveenraj44125-creator' in response_text:
            print("✅ GitHub username correctly displayed in configuration")
        else:
            print("⚠️  GitHub username not found in configuration display")
        
        print("\n🎉 All tests passed! GitHub username fix working correctly")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_missing_github_username():
    """Test that MCP server properly validates missing github_username"""
    
    print("\n🔍 Test 2: Testing validation for missing github_username...")
    
    mcp_url = "http://3.81.56.119:3000"
    
    try:
        setup_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": {
                    "mode": "fully_automated",
                    "app_type": "nodejs",
                    "app_name": "test-app"
                    # Missing github_username
                }
            }
        }
        
        # Try different endpoints
        endpoints = ["/sse", "/message", "/api"]
        response = None
        
        for endpoint in endpoints:
            try:
                response = requests.post(f"{mcp_url}{endpoint}", json=setup_payload, timeout=30)
                if response.status_code == 200:
                    break
            except:
                continue
        
        if not response or response.status_code != 200:
            print(f"❌ Failed to call setup_complete_deployment")
            return False
        
        result_data = response.json()
        
        # Should get an error about missing github_username
        if 'error' in result_data or 'github_username is required' in str(result_data):
            print("✅ Correctly validates missing github_username parameter")
            return True
        else:
            content = result_data.get('result', {}).get('content', [])
            if content and 'github_username is required' in content[0].get('text', ''):
                print("✅ Correctly validates missing github_username parameter")
                return True
            else:
                print("❌ Should have failed validation for missing github_username")
                return False
        
    except Exception as e:
        print(f"❌ Error in validation test: {e}")
        return False

if __name__ == "__main__":
    success1 = test_github_username_fix()
    success2 = test_missing_github_username()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All GitHub username tests passed!")
        print("✅ OIDC setup will now work correctly with full repository paths")
    else:
        print("❌ Some tests failed")
    
    sys.exit(0 if (success1 and success2) else 1)