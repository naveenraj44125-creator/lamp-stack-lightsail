#!/usr/bin/env python3

"""
Final test for MCP server OIDC fix using proper SSE client
"""

import requests
import json
import time
import uuid

def test_mcp_server_with_sse():
    """Test MCP server using SSE protocol"""
    
    print("🧪 Testing MCP Server OIDC Fix with SSE")
    print("=" * 50)
    
    try:
        # Step 1: Connect to SSE endpoint
        print("📡 Connecting to SSE endpoint...")
        sse_url = "http://3.81.56.119:3000/sse"
        
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        
        response = requests.get(sse_url, headers=headers, stream=True, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ SSE connection failed: {response.status_code}")
            return False
        
        print("✅ SSE connection established")
        
        # Step 2: Parse SSE response to get session endpoint
        session_endpoint = None
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                endpoint = line[6:]  # Remove 'data: ' prefix
                if endpoint.startswith('/message'):
                    session_endpoint = endpoint
                    print(f"✅ Got session endpoint: {endpoint}")
                    break
        
        if not session_endpoint:
            print("❌ Could not get session endpoint")
            return False
        
        # Step 3: Send MCP request
        message_url = f"http://3.81.56.119:3000{session_endpoint}"
        
        # Test the setup_complete_deployment tool with OIDC parameters
        mcp_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": {
                    "mode": "fully_automated",
                    "aws_region": "us-east-1",
                    "app_version": "1.0.0",
                    "app_type": "nodejs",
                    "app_name": "social-media-app-deployment",
                    "github_username": "naveenraj44125-creator",
                    "github_repo": "social-media-app-deployment",
                    "repo_visibility": "public"
                }
            }
        }
        
        print("📤 Sending MCP request...")
        print(f"   - Tool: setup_complete_deployment")
        print(f"   - Mode: fully_automated")
        print(f"   - GitHub Username: naveenraj44125-creator")
        print(f"   - GitHub Repo: social-media-app-deployment")
        
        response = requests.post(message_url, json=mcp_request, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ MCP request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        if 'error' in result:
            print(f"❌ MCP Error: {result['error']}")
            return False
        
        # Step 4: Analyze the response
        print("✅ MCP request successful")
        
        content = result.get('result', {}).get('content', [])
        if not content:
            print("❌ No content in response")
            return False
        
        response_text = content[0].get('text', '')
        
        print("\n📋 Analyzing GITHUB_REPO in response...")
        
        # Look for GITHUB_REPO export
        if 'export GITHUB_REPO=' in response_text:
            lines = response_text.split('\n')
            github_repo_lines = [line for line in lines if 'export GITHUB_REPO=' in line]
            
            for line in github_repo_lines:
                print(f"Found: {line.strip()}")
                
                # Check if it has the correct format
                if 'naveenraj44125-creator/social-media-app-deployment' in line:
                    print("✅ GITHUB_REPO has correct format with username!")
                    print("✅ OIDC issue is FIXED!")
                    return True
                elif 'social-media-app-deployment' in line and 'naveenraj44125-creator' not in line:
                    print("❌ GITHUB_REPO missing username prefix!")
                    print("Expected: naveenraj44125-creator/social-media-app-deployment")
                    print(f"Got: {line.strip()}")
                    return False
        else:
            print("❌ GITHUB_REPO export not found in response")
            # Print first few lines of response for debugging
            print("\n🔍 Response preview:")
            lines = response_text.split('\n')[:10]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            return False
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_server_status():
    """Check basic server status"""
    
    print("🔍 Checking Server Status")
    print("=" * 30)
    
    try:
        response = requests.get("http://3.81.56.119:3000/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Server is accessible")
            
            html = response.text
            
            # Look for version info
            if '1.1.1' in html:
                print("✅ Server version 1.1.1 detected")
            elif '1.1.0' in html:
                print("⚠️  Server still on version 1.1.0")
            else:
                print("⚠️  Server version unclear")
            
            # Look for github_username
            if 'github_username' in html.lower():
                print("✅ github_username parameter found")
            else:
                print("❌ github_username parameter not found")
            
            return True
        else:
            print(f"❌ Server not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Final MCP Server OIDC Fix Test")
    print("=" * 50)
    
    server_ok = check_server_status()
    
    if server_ok:
        success = test_mcp_server_with_sse()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 OIDC ISSUE IS FIXED!")
            print("✅ GITHUB_REPO correctly includes username")
            print("✅ Format: naveenraj44125-creator/social-media-app-deployment")
            print("\n📋 Summary:")
            print("   • MCP server properly handles github_username parameter")
            print("   • Full repository path is constructed correctly")
            print("   • OIDC setup will work with GitHub Actions")
        else:
            print("❌ OIDC issue still exists or test failed")
            print("🔧 May need further investigation")
    else:
        print("\n❌ Cannot test - server not accessible")
        
    exit(0 if (server_ok and success) else 1)