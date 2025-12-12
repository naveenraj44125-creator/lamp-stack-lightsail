#!/usr/bin/env python3

"""
Simple test to check if the current MCP server has github_username parameter
"""

import requests
import json

def test_server_capabilities():
    """Test what the current server can do"""
    
    print("🔍 Testing Current MCP Server Capabilities")
    print("=" * 45)
    
    try:
        # Try to access the server health endpoint
        health_response = requests.get("http://3.81.56.119:3000/health", timeout=10)
        print(f"Health endpoint: {health_response.status_code}")
        
        # Try to access SSE endpoint and see what happens
        sse_response = requests.get("http://3.81.56.119:3000/sse", timeout=5)
        print(f"SSE endpoint: {sse_response.status_code}")
        
        if sse_response.status_code == 200:
            # Try to read the first few lines
            content = sse_response.text[:500]
            print("SSE Response preview:")
            print(content)
            
            # Look for session endpoint
            if '/message' in content:
                # Extract session endpoint
                lines = content.split('\n')
                for line in lines:
                    if 'data: ' in line and '/message' in line:
                        session_endpoint = line.replace('data: ', '').strip()
                        print(f"Found session endpoint: {session_endpoint}")
                        
                        # Try to call the session endpoint
                        message_url = f"http://3.81.56.119:3000{session_endpoint}"
                        
                        # Test with a simple list tools request
                        list_request = {
                            "jsonrpc": "2.0",
                            "id": "test-123",
                            "method": "tools/list"
                        }
                        
                        print(f"Testing message endpoint: {message_url}")
                        msg_response = requests.post(message_url, json=list_request, timeout=10)
                        print(f"Message response: {msg_response.status_code}")
                        
                        if msg_response.status_code == 200:
                            result = msg_response.json()
                            print("✅ MCP communication working!")
                            
                            # Check for tools
                            tools = result.get('result', {}).get('tools', [])
                            print(f"Found {len(tools)} tools")
                            
                            # Look for setup_complete_deployment
                            for tool in tools:
                                if tool.get('name') == 'setup_complete_deployment':
                                    print("\n✅ Found setup_complete_deployment tool!")
                                    
                                    # Check parameters
                                    schema = tool.get('inputSchema', {})
                                    properties = schema.get('properties', {})
                                    
                                    if 'github_username' in properties:
                                        print("✅ github_username parameter EXISTS!")
                                        print(f"   Description: {properties['github_username'].get('description', 'N/A')}")
                                        
                                        # Now test the actual call
                                        return test_oidc_call(message_url)
                                    else:
                                        print("❌ github_username parameter NOT found")
                                        print("Available parameters:", list(properties.keys())[:10])
                                        return False
                            
                            print("❌ setup_complete_deployment tool not found")
                            return False
                        else:
                            print(f"❌ Message endpoint failed: {msg_response.text}")
                            return False
                        
                        break
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_oidc_call(message_url):
    """Test the actual OIDC call"""
    
    print("\n🧪 Testing OIDC Call")
    print("=" * 25)
    
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": "oidc-test-456",
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
        
        print("📤 Calling setup_complete_deployment with OIDC parameters...")
        
        response = requests.post(message_url, json=mcp_request, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
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
        
        # Look for GITHUB_REPO
        if 'export GITHUB_REPO=' in response_text:
            lines = response_text.split('\n')
            for line in lines:
                if 'export GITHUB_REPO=' in line:
                    print(f"Found GITHUB_REPO: {line.strip()}")
                    
                    if 'naveenraj44125-creator/social-media-app-deployment' in line:
                        print("✅ OIDC FORMAT IS CORRECT!")
                        return True
                    elif 'social-media-app-deployment' in line:
                        print("❌ Missing username in GITHUB_REPO")
                        return False
        
        print("❌ GITHUB_REPO not found in response")
        print("Response preview:", response_text[:300])
        return False
        
    except Exception as e:
        print(f"❌ Error in OIDC call: {e}")
        return False

def main():
    print("🔧 Simple MCP Server OIDC Check")
    print("=" * 50)
    print("Checking if current server already has OIDC fix...")
    print()
    
    success = test_server_capabilities()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OIDC IS ALREADY WORKING!")
        print("✅ The issue was already resolved!")
        print("✅ No need to wait for deployment!")
    else:
        print("❌ OIDC issue still exists")
        print("💡 Need to wait for server deployment")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)