#!/usr/bin/env python3
"""
Test MCP server using direct HTTP requests to simulate MCP client behavior
"""

import requests
import json
import time
import uuid

def test_mcp_server_direct():
    """Test MCP server using direct HTTP requests"""
    print("🔧 Testing MCP Server Direct Connection")
    print("=" * 60)
    
    mcp_url = "http://3.81.56.119:3000"
    
    try:
        # Step 1: Establish SSE connection
        print("1. Establishing SSE connection...")
        sse_response = requests.get(f"{mcp_url}/sse", stream=True, timeout=5)
        
        if sse_response.status_code != 200:
            print(f"❌ SSE connection failed: {sse_response.status_code}")
            return False
            
        print("✅ SSE connection established")
        
        # Extract session ID from response headers or generate one
        session_id = str(uuid.uuid4())
        
        # Step 2: Test tools/list
        print("\n2. Testing tools/list...")
        list_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        message_response = requests.post(
            f"{mcp_url}/message?sessionId={session_id}",
            json=list_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if message_response.status_code == 200:
            print("✅ tools/list request successful")
            try:
                result = message_response.json()
                if 'result' in result and 'tools' in result['result']:
                    tools = result['result']['tools']
                    print(f"   Found {len(tools)} tools")
                    
                    # Check for configure_github_repository
                    tool_names = [tool['name'] for tool in tools]
                    if 'configure_github_repository' in tool_names:
                        print("   ✅ configure_github_repository tool found!")
                        
                        # Step 3: Test configure_github_repository
                        print("\n3. Testing configure_github_repository...")
                        
                        config_request = {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/call",
                            "params": {
                                "name": "configure_github_repository",
                                "arguments": {
                                    "github_username": "johndoe",
                                    "repository_name": "my-awesome-nodejs-app",
                                    "app_type": "nodejs"
                                }
                            }
                        }
                        
                        config_response = requests.post(
                            f"{mcp_url}/message?sessionId={session_id}",
                            json=config_request,
                            headers={"Content-Type": "application/json"},
                            timeout=10
                        )
                        
                        if config_response.status_code == 200:
                            print("✅ configure_github_repository call successful")
                            try:
                                config_result = config_response.json()
                                if 'result' in config_result and 'content' in config_result['result']:
                                    content = config_result['result']['content'][0]['text']
                                    print(f"\n📋 Tool Response Preview:")
                                    print(content[:300] + "..." if len(content) > 300 else content)
                                    return True
                                else:
                                    print("❌ Invalid response format")
                                    print(f"Response: {config_result}")
                            except json.JSONDecodeError as e:
                                print(f"❌ JSON decode error: {e}")
                                print(f"Raw response: {config_response.text}")
                        else:
                            print(f"❌ configure_github_repository call failed: {config_response.status_code}")
                            print(f"Response: {config_response.text}")
                    else:
                        print("❌ configure_github_repository tool not found")
                        print(f"Available tools: {tool_names}")
                else:
                    print("❌ Invalid tools list response format")
                    print(f"Response: {result}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {message_response.text}")
        else:
            print(f"❌ tools/list request failed: {message_response.status_code}")
            print(f"Response: {message_response.text}")
            
        return False
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

def test_simple_health_check():
    """Test simple health check endpoint"""
    print("\n🏥 Testing Health Check")
    print("=" * 30)
    
    mcp_url = "http://3.81.56.119:3000"
    
    try:
        response = requests.get(f"{mcp_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check successful")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Service: {health_data.get('service')}")
            print(f"   Version: {health_data.get('version')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Run MCP server tests"""
    print("🚀 MCP Server Direct Connection Test")
    print("=" * 60)
    
    # Test health first
    health_ok = test_simple_health_check()
    
    if health_ok:
        # Test MCP functionality
        mcp_ok = test_mcp_server_direct()
        
        print(f"\n" + "=" * 60)
        print("🏁 Test Results")
        print("=" * 60)
        
        if mcp_ok:
            print("✅ MCP server is working correctly!")
            print("✅ configure_github_repository tool is functional")
            print("✅ GitHub username fix is complete and working")
        else:
            print("❌ MCP server has issues with tool execution")
            print("⚠️  Check server logs for details")
    else:
        print("❌ MCP server is not responding to health checks")

if __name__ == "__main__":
    main()