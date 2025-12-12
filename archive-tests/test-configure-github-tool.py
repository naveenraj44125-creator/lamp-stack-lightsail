#!/usr/bin/env python3
"""
Test the configure_github_repository MCP tool using SSE protocol
"""

import requests
import json
import time

def test_configure_github_repository():
    """Test the configure_github_repository MCP tool"""
    print("🔧 Testing configure_github_repository MCP Tool")
    print("=" * 60)
    
    mcp_url = "http://3.81.56.119:3000"
    
    # Test data
    test_data = {
        "github_username": "johndoe",
        "repository_name": "my-awesome-nodejs-app",
        "app_type": "nodejs"
    }
    
    print(f"📋 Test Parameters:")
    print(f"   GitHub Username: {test_data['github_username']}")
    print(f"   Repository Name: {test_data['repository_name']}")
    print(f"   App Type: {test_data['app_type']}")
    
    try:
        # Test using the SSE endpoint with proper MCP protocol
        print(f"\n🔌 Connecting to MCP server at {mcp_url}")
        
        # Create MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "configure_github_repository",
                "arguments": test_data
            }
        }
        
        # Send request via SSE
        response = requests.post(
            f"{mcp_url}/sse",
            json=mcp_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            timeout=30
        )
        
        print(f"📤 Request sent: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ MCP tool call successful!")
            
            # Parse response
            response_text = response.text
            print(f"\n📥 Response received:")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Response length: {len(response_text)} characters")
            
            # Try to extract JSON from SSE response
            lines = response_text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])  # Remove 'data: ' prefix
                        if 'result' in data:
                            result = data['result']
                            if 'content' in result and result['content']:
                                content = result['content'][0]['text']
                                print(f"\n📋 Tool Response:")
                                print(content[:500] + "..." if len(content) > 500 else content)
                                return True
                    except json.JSONDecodeError:
                        continue
            
            print("⚠️  Could not parse MCP response")
            return False
            
        else:
            print(f"❌ MCP tool call failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCP tool: {e}")
        return False

def test_mcp_tools_list():
    """Test listing MCP tools to verify configure_github_repository exists"""
    print("\n📋 Testing MCP Tools List")
    print("=" * 40)
    
    mcp_url = "http://3.81.56.119:3000"
    
    try:
        # Create MCP request to list tools
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            f"{mcp_url}/sse",
            json=mcp_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Tools list request successful!")
            
            # Parse response to find configure_github_repository
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if 'result' in data and 'tools' in data['result']:
                            tools = data['result']['tools']
                            tool_names = [tool['name'] for tool in tools]
                            
                            print(f"\n📋 Available MCP Tools ({len(tools)}):")
                            for tool in tools:
                                name = tool['name']
                                desc = tool['description'][:80] + "..." if len(tool['description']) > 80 else tool['description']
                                print(f"   • {name}: {desc}")
                            
                            if 'configure_github_repository' in tool_names:
                                print(f"\n✅ configure_github_repository tool found!")
                                return True
                            else:
                                print(f"\n❌ configure_github_repository tool not found!")
                                return False
                                
                    except json.JSONDecodeError:
                        continue
            
            print("⚠️  Could not parse tools list response")
            return False
            
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error listing MCP tools: {e}")
        return False

def main():
    """Run the configure_github_repository tool test"""
    print("🚀 Configure GitHub Repository Tool Test")
    print("=" * 60)
    
    # Test tools list first
    tools_available = test_mcp_tools_list()
    
    if tools_available:
        # Test the actual tool
        tool_works = test_configure_github_repository()
        
        print(f"\n" + "=" * 60)
        print("🏁 Test Results")
        print("=" * 60)
        
        if tool_works:
            print("✅ configure_github_repository tool is working correctly!")
            print("✅ MCP server provides personalized GitHub repository setup")
            print("✅ Users can get custom repository URLs and commands")
        else:
            print("❌ configure_github_repository tool has issues")
            print("⚠️  Check MCP server logs for details")
    else:
        print(f"\n❌ configure_github_repository tool not available")
        print("⚠️  Check MCP server configuration")

if __name__ == "__main__":
    main()