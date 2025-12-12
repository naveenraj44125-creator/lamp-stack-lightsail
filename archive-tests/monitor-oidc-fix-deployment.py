#!/usr/bin/env python3

"""
Monitor the OIDC fix deployment and test it once deployed
"""

import requests
import time
import json
import uuid

def check_server_version():
    """Check if server has been updated to version 1.1.2"""
    
    try:
        response = requests.get("http://3.81.56.119:3000/", timeout=10)
        
        if response.status_code != 200:
            return False, "not_accessible"
        
        html = response.text
        
        if 'Version 1.1.2' in html:
            return True, "1.1.2"
        elif 'Version 1.1.1' in html:
            return True, "1.1.1"
        elif 'Version 1.1.0' in html:
            return True, "1.1.0"
        else:
            return True, "unknown"
            
    except Exception as e:
        return False, "error"

def test_oidc_fix_with_sse():
    """Test the OIDC fix using SSE protocol"""
    
    print("🧪 Testing OIDC Fix with SSE")
    print("=" * 35)
    
    try:
        # Step 1: Connect to SSE
        sse_url = "http://3.81.56.119:3000/sse"
        headers = {'Accept': 'text/event-stream', 'Cache-Control': 'no-cache'}
        
        response = requests.get(sse_url, headers=headers, stream=True, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ SSE connection failed: {response.status_code}")
            return False
        
        # Step 2: Get session endpoint
        session_endpoint = None
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: ') and '/message' in line:
                session_endpoint = line[6:]  # Remove 'data: ' prefix
                break
        
        if not session_endpoint:
            print("❌ Could not get session endpoint")
            return False
        
        # Step 3: Test MCP request
        message_url = f"http://3.81.56.119:3000{session_endpoint}"
        
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
        
        print("📤 Testing MCP request...")
        response = requests.post(message_url, json=mcp_request, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ MCP request failed: {response.status_code}")
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
        
        # Look for GITHUB_REPO with correct format
        if 'export GITHUB_REPO=' in response_text:
            lines = response_text.split('\n')
            github_repo_lines = [line for line in lines if 'export GITHUB_REPO=' in line]
            
            for line in github_repo_lines:
                if 'naveenraj44125-creator/social-media-app-deployment' in line:
                    print("✅ GITHUB_REPO has correct format!")
                    print(f"   Found: {line.strip()}")
                    return True
                elif 'social-media-app-deployment' in line:
                    print("❌ GITHUB_REPO still missing username!")
                    print(f"   Found: {line.strip()}")
                    return False
        
        print("❌ GITHUB_REPO not found in response")
        return False
        
    except Exception as e:
        print(f"❌ Error testing OIDC fix: {e}")
        return False

def monitor_deployment():
    """Monitor deployment and test OIDC fix"""
    
    print("🚀 OIDC Fix Deployment Monitor")
    print("=" * 50)
    print("Monitoring for MCP server version 1.1.2...")
    print("GitHub Actions: https://github.com/naveenraj44125-creator/lamp-stack-lightsail/actions")
    print()
    
    max_attempts = 15  # 7.5 minutes
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"📊 Check #{attempt} ({time.strftime('%H:%M:%S')})")
        print("-" * 30)
        
        accessible, version = check_server_version()
        
        if not accessible:
            print("🔄 Server not accessible (deployment may be restarting)")
        else:
            print(f"✅ Server accessible - Version: {version}")
            
            if version == "1.1.2":
                print("🎉 Server updated to version 1.1.2!")
                
                # Test the OIDC fix
                if test_oidc_fix_with_sse():
                    print("\n🎉 OIDC FIX SUCCESSFUL!")
                    print("✅ GITHUB_REPO now includes username")
                    print("✅ Format: naveenraj44125-creator/social-media-app-deployment")
                    print("\n📋 Issue Resolution:")
                    print("   • MCP server properly handles github_username parameter")
                    print("   • Full repository path constructed correctly")
                    print("   • OIDC setup will work with GitHub Actions")
                    return True
                else:
                    print("\n⚠️  Server updated but OIDC fix test failed")
                    return False
            else:
                print(f"⏳ Waiting for version 1.1.2 (current: {version})")
        
        if attempt < max_attempts:
            print("⏰ Waiting 30 seconds...")
            time.sleep(30)
    
    print("\n⏰ Monitoring timeout reached")
    return False

if __name__ == "__main__":
    success = monitor_deployment()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OIDC ISSUE RESOLVED!")
        print("✅ The MCP server now correctly handles the repository format")
        print("✅ GitHub Actions OIDC authentication will work properly")
    else:
        print("❌ OIDC issue not resolved yet")
        print("💡 Check GitHub Actions or try manual server restart")
    
    exit(0 if success else 1)