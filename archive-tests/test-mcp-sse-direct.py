#!/usr/bin/env python3

"""
Test MCP server using SSE endpoint directly
"""

import requests
import json
import time

def test_mcp_sse_endpoint():
    """Test the MCP server using SSE endpoint"""
    
    print("🧪 Testing MCP Server SSE Endpoint")
    print("=" * 50)
    
    try:
        # Try the SSE endpoint
        url = "http://3.81.56.119:3000/sse"
        
        # First, try to establish SSE connection
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        
        print("📡 Connecting to SSE endpoint...")
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ SSE connection failed: {response.status_code}")
            return False
        
        print("✅ SSE connection established")
        
        # Read initial messages
        lines_read = 0
        for line in response.iter_lines(decode_unicode=True):
            if line:
                print(f"SSE: {line}")
                lines_read += 1
                if lines_read > 5:  # Don't read forever
                    break
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_web_interface_content():
    """Check what's actually in the web interface"""
    
    print("\n🔍 Analyzing Web Interface Content")
    print("=" * 40)
    
    try:
        response = requests.get("http://3.81.56.119:3000/", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to get web interface: {response.status_code}")
            return False
        
        html = response.text
        
        # Look for key indicators
        indicators = [
            ('github_username', 'GitHub username parameter'),
            ('setup_complete_deployment', 'Setup deployment tool'),
            ('Version 1.1.0', 'Server version'),
            ('OIDC', 'OIDC setup'),
            ('fully_automated', 'Fully automated mode')
        ]
        
        for indicator, description in indicators:
            if indicator in html:
                print(f"✅ Found: {description}")
            else:
                print(f"❌ Missing: {description}")
        
        # Check for any version info
        if 'version' in html.lower():
            print("\n📋 Version information found in HTML")
        
        # Look for tool definitions
        if 'tools' in html.lower():
            print("✅ Tool definitions found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_github_actions_status():
    """Check if there are any pending GitHub Actions"""
    
    print("\n🔍 Checking GitHub Actions Status")
    print("=" * 35)
    
    try:
        # This would require GitHub API, but let's just check if we can determine
        # if the server was recently updated
        
        print("💡 To check GitHub Actions status:")
        print("   Visit: https://github.com/naveenraj44125-creator/lamp-stack-lightsail/actions")
        print("   Look for recent 'Deploy MCP Server' workflows")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 MCP Server SSE Direct Test")
    print("=" * 50)
    
    web_check = test_web_interface_content()
    sse_check = test_mcp_sse_endpoint()
    check_github_actions_status()
    
    print("\n" + "=" * 50)
    if web_check:
        print("🎯 Web interface accessible")
    if sse_check:
        print("🎯 SSE endpoint accessible")
    
    print("\n💡 Next steps:")
    print("   1. Check if latest commit was deployed")
    print("   2. Verify GitHub Actions completed successfully")
    print("   3. Test MCP server with proper SSE client")