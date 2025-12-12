#!/usr/bin/env python3
"""
Real MCP server functionality test - makes actual HTTP requests to test tools
"""

import requests
import json
import time

def test_mcp_tools_real():
    """Test actual MCP server tools via HTTP requests"""
    
    base_url = "http://3.81.56.119:3000"
    
    print("🧪 Testing Real MCP Server Tools")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health: {health_data}")
        else:
            print(f"   ❌ Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health error: {e}")
        return False
    
    # Test 2: Web interface
    print("\n2. Testing web interface...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Web interface accessible (length: {len(response.text)} chars)")
        else:
            print(f"   ❌ Web interface failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Web interface error: {e}")
    
    # Test 3: SSE endpoint (just check if it responds)
    print("\n3. Testing SSE endpoint...")
    try:
        response = requests.get(f"{base_url}/sse", timeout=5, stream=True)
        print(f"   ✅ SSE endpoint responds: {response.status_code}")
        if response.status_code == 200:
            print(f"   📡 Content-Type: {response.headers.get('content-type', 'unknown')}")
    except Exception as e:
        print(f"   ⚠️  SSE endpoint: {e}")
    
    # Test 4: Try to make an MCP message request
    print("\n4. Testing MCP message endpoint...")
    try:
        # Test list tools request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            f"{base_url}/message",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ MCP tools/list successful")
            if 'result' in result and 'tools' in result['result']:
                tools = result['result']['tools']
                print(f"   📋 Found {len(tools)} tools:")
                for tool in tools:
                    print(f"      • {tool['name']}: {tool.get('description', 'No description')[:60]}...")
            else:
                print(f"   📋 Response: {result}")
        else:
            print(f"   ❌ MCP request failed: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ MCP request error: {e}")
    
    # Test 5: Test a specific tool
    print("\n5. Testing setup_complete_deployment tool...")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": {
                    "mode": "help"
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/message",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Tool call successful")
            if 'result' in result and 'content' in result['result']:
                content = result['result']['content'][0]['text']
                print(f"   📄 Response length: {len(content)} characters")
                # Show first few lines
                lines = content.split('\n')[:5]
                for line in lines:
                    if line.strip():
                        print(f"      {line[:80]}...")
                        break
            else:
                print(f"   📋 Response: {result}")
        else:
            print(f"   ❌ Tool call failed: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Tool call error: {e}")
    
    # Test 6: Test fully automated mode
    print("\n6. Testing fully automated mode...")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": {
                    "mode": "fully_automated",
                    "app_type": "nodejs",
                    "app_name": "test-api",
                    "instance_name": "test-instance",
                    "aws_region": "us-east-1",
                    "app_version": "1.0.0",
                    "database_type": "postgresql",
                    "enable_bucket": True,
                    "bucket_name": "test-bucket"
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/message",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Fully automated mode successful")
            if 'result' in result and 'content' in result['result']:
                content = result['result']['content'][0]['text']
                print(f"   📄 Response length: {len(content)} characters")
                # Check for key indicators
                if "FULLY_AUTOMATED" in content:
                    print(f"   🤖 Fully automated mode detected")
                if "nodejs" in content.lower():
                    print(f"   📦 Node.js configuration detected")
                if "postgresql" in content.lower():
                    print(f"   🗄️  PostgreSQL configuration detected")
            else:
                print(f"   📋 Response: {result}")
        else:
            print(f"   ❌ Fully automated mode failed: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Fully automated mode error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Real MCP server testing completed!")
    
    return True

if __name__ == "__main__":
    test_mcp_tools_real()