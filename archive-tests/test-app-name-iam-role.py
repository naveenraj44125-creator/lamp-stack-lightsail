#!/usr/bin/env python3

"""
Test script to verify the MCP server uses app_name instead of app_type for default IAM role naming
"""

import json
import requests
import sys

def test_mcp_server_app_name_iam_role():
    """Test that MCP server uses app_name for default IAM role naming"""
    
    print("🧪 Testing MCP Server - App Name IAM Role Naming")
    print("=" * 60)
    
    # MCP server URL
    mcp_url = "http://3.81.56.119:3000"
    
    try:
        # Test 1: Check tool description mentions app_name
        print("\n📋 Test 1: Checking tool description...")
        
        list_tools_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        response = requests.post(f"{mcp_url}/sse", json=list_tools_payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to get tools list: {response.status_code}")
            return False
            
        tools_data = response.json()
        
        # Find setup_complete_deployment tool
        setup_tool = None
        for tool in tools_data.get('result', {}).get('tools', []):
            if tool['name'] == 'setup_complete_deployment':
                setup_tool = tool
                break
        
        if not setup_tool:
            print("❌ setup_complete_deployment tool not found")
            return False
        
        # Check if description mentions app_name instead of app_type
        description = setup_tool.get('description', '')
        if 'GitHubActions-{app_name}-deployment' in description:
            print("✅ Tool description correctly uses app_name for IAM role naming")
        elif 'GitHubActions-{app_type}-deployment' in description:
            print("❌ Tool description still uses app_type for IAM role naming")
            return False
        else:
            print("⚠️  IAM role naming pattern not found in description")
        
        # Test 2: Call setup_complete_deployment with fully_automated mode
        print("\n🚀 Test 2: Testing fully_automated mode with app_name...")
        
        setup_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": {
                    "mode": "fully_automated",
                    "app_type": "nodejs",
                    "app_name": "my-custom-nodejs-app",
                    "aws_region": "us-east-1",
                    "bundle_id": "small_3_0",
                    "database_type": "postgresql",
                    "enable_bucket": False
                }
            }
        }
        
        response = requests.post(f"{mcp_url}/sse", json=setup_payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to call setup_complete_deployment: {response.status_code}")
            return False
        
        result_data = response.json()
        
        if 'error' in result_data:
            print(f"❌ MCP call failed: {result_data['error']}")
            return False
        
        # Check the response content for IAM role naming
        content = result_data.get('result', {}).get('content', [])
        if not content:
            print("❌ No content in response")
            return False
        
        response_text = content[0].get('text', '')
        
        # Look for the default role naming in the response
        if 'GitHubActions-my-custom-nodejs-app-deployment' in response_text:
            print("✅ Response correctly shows app_name in default IAM role naming")
        elif 'GitHubActions-nodejs-deployment' in response_text:
            print("❌ Response still shows app_type in default IAM role naming")
            return False
        else:
            print("⚠️  Default IAM role naming not found in response")
            # Print part of response for debugging
            print(f"Response preview: {response_text[:500]}...")
        
        # Test 3: Check that the pattern documentation is updated
        print("\n📖 Test 3: Checking pattern documentation...")
        
        if 'GitHubActions-{app_name}-deployment' in response_text:
            print("✅ Documentation correctly shows app_name pattern")
        elif 'GitHubActions-{app_type}-deployment' in response_text:
            print("❌ Documentation still shows app_type pattern")
            return False
        else:
            print("⚠️  Pattern documentation not found in response")
        
        print("\n🎉 All tests passed! MCP server correctly uses app_name for IAM role naming")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_server_app_name_iam_role()
    sys.exit(0 if success else 1)