#!/usr/bin/env python3

"""
Monitor the OIDC fix deployment for version 1.1.3 and test it once deployed
"""

import requests
import time
import json
import uuid

def check_server_version():
    """Check if server has been updated to version 1.1.3"""
    
    try:
        response = requests.get("http://3.81.56.119:3000/", timeout=10)
        
        if response.status_code != 200:
            return False, "not_accessible"
        
        html = response.text
        
        if 'Version 1.1.3' in html:
            return True, "1.1.3"
        elif 'Version 1.1.2' in html:
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
        
        # Step 3: Test MCP request with the exact parameters that were failing
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
        
        print("📤 Testing MCP request with OIDC parameters...")
        print(f"   - github_username: {mcp_request['params']['arguments']['github_username']}")
        print(f"   - github_repo: {mcp_request['params']['arguments']['github_repo']}")
        print(f"   - app_name: {mcp_request['params']['arguments']['app_name']}")
        
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
                    
                    # Also check for other environment variables
                    print("\n📋 Key Environment Variables:")
                    for env_line in lines:
                        if any(var in env_line for var in ['export GITHUB_REPO=', 'export APP_NAME=', 'export APP_TYPE=']):
                            print(f"   {env_line.strip()}")
                    
                    return True
                elif 'social-media-app-deployment' in line and 'naveenraj44125-creator' not in line:
                    print("❌ GITHUB_REPO still missing username!")
                    print(f"   Found: {line.strip()}")
                    print("   Expected: export GITHUB_REPO=\"naveenraj44125-creator/social-media-app-deployment\"")
                    return False
        
        print("❌ GITHUB_REPO not found in response")
        print("📄 Response preview:")
        print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
        return False
        
    except Exception as e:
        print(f"❌ Error testing OIDC fix: {e}")
        return False

def monitor_deployment():
    """Monitor deployment and test OIDC fix"""
    
    print("🚀 OIDC Fix Deployment Monitor v1.1.3")
    print("=" * 50)
    print("Monitoring for MCP server version 1.1.3...")
    print("GitHub Actions: https://github.com/naveenraj44125-creator/lamp-stack-lightsail/actions")
    print("Latest commit: d7fa61e (Force MCP server deployment with OIDC fix)")
    print()
    
    max_attempts = 20  # 10 minutes
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
            
            if version == "1.1.3":
                print("🎉 Server updated to version 1.1.3!")
                
                # Test the OIDC fix
                if test_oidc_fix_with_sse():
                    print("\n🎉 OIDC FIX SUCCESSFUL!")
                    print("✅ GITHUB_REPO now includes username")
                    print("✅ Format: naveenraj44125-creator/social-media-app-deployment")
                    print("\n📋 Issue Resolution Summary:")
                    print("   • MCP server properly handles github_username parameter")
                    print("   • Full repository path constructed correctly")
                    print("   • OIDC setup will work with GitHub Actions")
                    print("   • Environment variables generated correctly")
                    print("\n🔧 Technical Details:")
                    print("   • MCP server uses external setup script for OIDC")
                    print("   • MCP generates environment variables including GITHUB_REPO")
                    print("   • Setup script uses GITHUB_REPO for IAM role trust policy")
                    print("   • Fixed: github_username parameter now properly constructs full path")
                    return True
                else:
                    print("\n⚠️  Server updated but OIDC fix test failed")
                    return False
            else:
                print(f"⏳ Waiting for version 1.1.3 (current: {version})")
        
        if attempt < max_attempts:
            print("⏰ Waiting 30 seconds...")
            time.sleep(30)
    
    print("\n⏰ Monitoring timeout reached")
    return False

if __name__ == "__main__":
    success = monitor_deployment()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OIDC ISSUE FULLY RESOLVED!")
        print("✅ The MCP server now correctly handles the repository format")
        print("✅ GitHub Actions OIDC authentication will work properly")
        print("✅ Fully automated deployments will include correct GITHUB_REPO")
    else:
        print("❌ OIDC issue not resolved yet")
        print("💡 Check GitHub Actions or investigate deployment process")
    
    exit(0 if success else 1)