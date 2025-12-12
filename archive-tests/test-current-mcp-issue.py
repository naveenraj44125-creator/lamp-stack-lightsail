#!/usr/bin/env python3

"""
Test the current MCP server to reproduce the OIDC issue
"""

import requests
import json

def test_mcp_server_oidc_issue():
    """Test the MCP server with the exact parameters from the user's issue"""
    
    print("🧪 Testing MCP Server OIDC Issue")
    print("=" * 50)
    
    # Test parameters from user's issue
    test_params = {
        "mode": "fully_automated",
        "aws_region": "us-east-1",
        "app_version": "1.0.0",
        "app_type": "nodejs",
        "app_name": "social-media-app-deployment",
        "instance_name": "social-media-app-deployment-instance",
        "blueprint_id": "ubuntu_22_04",
        "bundle_id": "small_3_0",
        "database_type": "postgresql",
        "db_external": True,
        "db_rds_name": "social-media-app-deployment-rds",
        "db_name": "nodejs_app_db",
        "enable_bucket": True,
        "bucket_name": "social-media-app-deployment-bucket",
        "bucket_access": "read_write",
        "bucket_bundle": "small_1_0",
        "github_username": "naveenraj44125-creator",
        "github_repo": "social-media-app-deployment",
        "repo_visibility": "public"
    }
    
    try:
        # Test the MCP server
        url = "http://3.81.56.119:3000/mcp"
        
        payload = {
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": test_params
            }
        }
        
        print(f"📡 Calling MCP server with parameters:")
        print(f"   - github_username: {test_params['github_username']}")
        print(f"   - github_repo: {test_params['github_repo']}")
        print(f"   - app_name: {test_params['app_name']}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        if 'error' in result:
            print(f"❌ MCP Error: {result['error']}")
            return False
        
        # Check the response content
        content = result.get('result', {}).get('content', [])
        if not content:
            print("❌ No content in response")
            return False
        
        response_text = content[0].get('text', '')
        
        print("\n📋 Checking GITHUB_REPO in response...")
        
        # Look for GITHUB_REPO export
        if 'export GITHUB_REPO=' in response_text:
            # Extract the GITHUB_REPO line
            lines = response_text.split('\n')
            github_repo_lines = [line for line in lines if 'export GITHUB_REPO=' in line]
            
            for line in github_repo_lines:
                print(f"Found: {line.strip()}")
                
                # Check if it has the correct format
                if 'naveenraj44125-creator/social-media-app-deployment' in line:
                    print("✅ GITHUB_REPO has correct format with username!")
                    return True
                elif 'social-media-app-deployment' in line and 'naveenraj44125-creator' not in line:
                    print("❌ GITHUB_REPO missing username prefix!")
                    print("Expected: naveenraj44125-creator/social-media-app-deployment")
                    print(f"Got: {line.strip()}")
                    return False
        else:
            print("❌ GITHUB_REPO export not found in response")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_server_version():
    """Check what version of the server is running"""
    
    print("\n🔍 Checking Server Version")
    print("=" * 30)
    
    try:
        response = requests.get("http://3.81.56.119:3000/", timeout=10)
        
        if response.status_code == 200:
            html = response.text
            if 'Version 1.1.0' in html:
                print("✅ Server running Version 1.1.0")
            else:
                print("⚠️  Server version not clearly identified")
                
            # Check for github_username in the interface
            if 'github_username' in html.lower():
                print("✅ github_username parameter visible in web interface")
            else:
                print("❌ github_username parameter not visible in web interface")
                
        else:
            print(f"❌ Failed to get server info: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking server: {e}")

if __name__ == "__main__":
    print("🔧 Current MCP Server OIDC Issue Test")
    print("=" * 50)
    
    check_server_version()
    success = test_mcp_server_oidc_issue()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OIDC issue is FIXED!")
        print("✅ GITHUB_REPO correctly includes username")
    else:
        print("❌ OIDC issue still exists")
        print("🔧 Need to investigate further")
        
    exit(0 if success else 1)