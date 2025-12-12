#!/usr/bin/env python3

"""
Test the current MCP server OIDC functionality to see if it works
even with the old server version, since the setup script has OIDC integration
"""

import requests
import time
import json
import uuid

def test_oidc_with_current_server():
    """Test OIDC with the current server using SSE protocol"""
    
    print("🧪 Testing OIDC with Current MCP Server")
    print("=" * 45)
    print("Theory: Setup script has OIDC integration, so it should work")
    print("even if MCP server version is old")
    print()
    
    try:
        # Step 1: Connect to SSE
        print("📡 Connecting to MCP server...")
        sse_url = "http://3.81.56.119:3000/sse"
        headers = {'Accept': 'text/event-stream', 'Cache-Control': 'no-cache'}
        
        response = requests.get(sse_url, headers=headers, stream=True, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ SSE connection failed: {response.status_code}")
            return False
        
        print("✅ SSE connection established")
        
        # Step 2: Get session endpoint
        session_endpoint = None
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: ') and '/message' in line:
                session_endpoint = line[6:]  # Remove 'data: ' prefix
                break
        
        if not session_endpoint:
            print("❌ Could not get session endpoint")
            return False
        
        print(f"✅ Session endpoint: {session_endpoint}")
        
        # Step 3: Test MCP request with github_username parameter
        message_url = f"http://3.81.56.119:3000{session_endpoint}"
        
        # Test 1: Check if github_username parameter exists
        print("\n🔍 Test 1: Check if github_username parameter exists")
        
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/list"
        }
        
        response = requests.post(message_url, json=list_tools_request, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get('result', {}).get('tools', [])
            
            setup_tool = None
            for tool in tools:
                if tool.get('name') == 'setup_complete_deployment':
                    setup_tool = tool
                    break
            
            if setup_tool:
                schema = setup_tool.get('inputSchema', {})
                properties = schema.get('properties', {})
                
                if 'github_username' in properties:
                    print("✅ github_username parameter exists in current server!")
                    print(f"   Description: {properties['github_username'].get('description', 'N/A')}")
                else:
                    print("❌ github_username parameter NOT found")
                    print("   Available parameters:", list(properties.keys()))
                    return False
            else:
                print("❌ setup_complete_deployment tool not found")
                return False
        else:
            print(f"❌ Failed to list tools: {response.status_code}")
            return False
        
        # Test 2: Try the actual OIDC setup call
        print("\n🔍 Test 2: Test OIDC setup call")
        
        mcp_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": {
                    "mode": "fully_automated",
                    "aws_region": "us-east-1",
                    "app_type": "nodejs",
                    "app_name": "social-media-app-deployment",
                    "github_username": "naveenraj44125-creator",
                    "github_repo": "social-media-app-deployment"
                }
            }
        }
        
        print("📤 Sending MCP request with parameters:")
        for key, value in mcp_request['params']['arguments'].items():
            print(f"   {key}: {value}")
        
        response = requests.post(message_url, json=mcp_request, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ MCP request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        
        if 'error' in result:
            print(f"❌ MCP Error: {result['error']}")
            return False
        
        # Check response content
        content = result.get('result', {}).get('content', [])
        if not content:
            print("❌ No content in response")
            return False
        
        response_text = content[0].get('text', '')
        
        # Analyze the response
        print("\n📋 Analyzing Response:")
        
        # Look for GITHUB_REPO environment variable
        if 'export GITHUB_REPO=' in response_text:
            lines = response_text.split('\n')
            github_repo_lines = [line for line in lines if 'export GITHUB_REPO=' in line]
            
            for line in github_repo_lines:
                print(f"   Found: {line.strip()}")
                
                if 'naveenraj44125-creator/social-media-app-deployment' in line:
                    print("✅ GITHUB_REPO has CORRECT format with username!")
                    
                    # Show other key environment variables
                    print("\n📋 Key Environment Variables:")
                    for env_line in lines:
                        if any(var in env_line for var in ['export GITHUB_REPO=', 'export APP_NAME=', 'export APP_TYPE=']):
                            print(f"   {env_line.strip()}")
                    
                    return True
                elif 'social-media-app-deployment' in line and 'naveenraj44125-creator' not in line:
                    print("❌ GITHUB_REPO missing username!")
                    print("   Expected: export GITHUB_REPO=\"naveenraj44125-creator/social-media-app-deployment\"")
                    return False
        else:
            print("❌ GITHUB_REPO not found in response")
            
        # Show response preview for debugging
        print("\n📄 Response Preview (first 800 chars):")
        print(response_text[:800] + "..." if len(response_text) > 800 else response_text)
        
        return False
        
    except Exception as e:
        print(f"❌ Error testing OIDC: {e}")
        return False

def main():
    print("🔧 Current MCP Server OIDC Test")
    print("=" * 50)
    print("Testing if OIDC works with current server version")
    print("Setup script URL: https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh")
    print()
    
    success = test_oidc_with_current_server()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OIDC ALREADY WORKS!")
        print("✅ Current MCP server properly handles github_username")
        print("✅ GITHUB_REPO format is correct")
        print("✅ No deployment needed - issue is already resolved!")
    else:
        print("❌ OIDC issue still exists")
        print("💡 Need to wait for MCP server deployment or investigate further")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)