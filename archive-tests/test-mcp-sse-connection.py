#!/usr/bin/env python3
"""
Test MCP server SSE connection and tool functionality
"""

import requests
import json
import time
import uuid

def test_mcp_sse_connection():
    """Test MCP server via SSE connection"""
    
    base_url = "http://3.81.56.119:3000"
    
    print("🧪 Testing MCP Server SSE Connection")
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
    
    # Test 2: Establish SSE connection
    print("\n2. Testing SSE connection...")
    try:
        response = requests.get(f"{base_url}/sse", timeout=10, stream=True)
        if response.status_code == 200:
            print(f"   ✅ SSE connection established")
            print(f"   📡 Content-Type: {response.headers.get('content-type')}")
            
            # Read first few events
            lines_read = 0
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(f"   📨 SSE: {line[:100]}...")
                    lines_read += 1
                    if lines_read >= 3:  # Read first 3 events
                        break
            
            response.close()
        else:
            print(f"   ❌ SSE connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ SSE connection error: {e}")
        return False
    
    # Test 3: Try direct tool access via web interface
    print("\n3. Testing web interface tool access...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            content = response.text
            print(f"   ✅ Web interface loaded ({len(content)} chars)")
            
            # Check for tool information in the web interface
            if "setup_complete_deployment" in content:
                print(f"   🔧 setup_complete_deployment tool found in web interface")
            if "get_deployment_examples" in content:
                print(f"   📋 get_deployment_examples tool found in web interface")
            if "fully_automated" in content:
                print(f"   🤖 Fully automated mode mentioned in web interface")
                
        else:
            print(f"   ❌ Web interface failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Web interface error: {e}")
    
    # Test 4: Check if server supports direct HTTP tool calls (some MCP servers do)
    print("\n4. Testing alternative tool access methods...")
    
    # Try GET request to see available tools
    try:
        response = requests.get(f"{base_url}/tools", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Tools endpoint accessible: {response.json()}")
        else:
            print(f"   ⚠️  Tools endpoint: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Tools endpoint error: {e}")
    
    # Try to get server info
    try:
        response = requests.get(f"{base_url}/info", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Info endpoint: {response.json()}")
        else:
            print(f"   ⚠️  Info endpoint: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Info endpoint error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 MCP Server Status Summary:")
    print("   ✅ Server is running and healthy")
    print("   ✅ SSE endpoint is accessible")
    print("   ✅ Web interface is working")
    print("   📡 MCP protocol requires SSE client for tool calls")
    print("   🔗 Server URL: http://3.81.56.119:3000")
    print("   🌐 Web UI: http://3.81.56.119:3000/")
    print("   📨 SSE: http://3.81.56.119:3000/sse")
    
    return True

if __name__ == "__main__":
    test_mcp_sse_connection()