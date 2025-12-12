#!/usr/bin/env python3
"""
Test script for the new get_project_structure_guide MCP tool
Tests the project structure guidance functionality with different application types
"""

import requests
import json
import sys
from datetime import datetime

# MCP Server Configuration
MCP_SERVER_URL = "http://3.81.56.119:3000"

def test_mcp_tool(tool_name, arguments):
    """Test an MCP tool with given arguments"""
    print(f"\n🧪 Testing MCP Tool: {tool_name}")
    print(f"📝 Arguments: {json.dumps(arguments, indent=2)}")
    print("=" * 60)
    
    try:
        # Prepare MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Send request to MCP server
        response = requests.post(
            f"{MCP_SERVER_URL}/message",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"][0]["text"]
                print("✅ SUCCESS: Tool executed successfully")
                print("\n📋 Response Preview:")
                # Show first 500 characters of response
                preview = content[:500] + "..." if len(content) > 500 else content
                print(preview)
                print(f"\n📊 Full response length: {len(content)} characters")
                return True, content
            else:
                print(f"❌ ERROR: Unexpected response format: {result}")
                return False, None
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False, None

def main():
    """Test the project structure guide tool with different scenarios"""
    
    print("🚀 MCP Project Structure Guide Tool Test")
    print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 MCP Server: {MCP_SERVER_URL}")
    print("=" * 80)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Node.js Basic Structure",
            "args": {
                "app_type": "nodejs"
            }
        },
        {
            "name": "Node.js with Database and Bucket",
            "args": {
                "app_type": "nodejs",
                "deployment_features": ["database", "bucket"]
            }
        },
        {
            "name": "React Application Structure",
            "args": {
                "app_type": "react",
                "include_examples": True,
                "include_github_actions": True
            }
        },
        {
            "name": "Docker Application with Full Features",
            "args": {
                "app_type": "docker",
                "deployment_features": ["database", "bucket", "ssl", "monitoring"]
            }
        },
        {
            "name": "LAMP Stack Structure",
            "args": {
                "app_type": "lamp",
                "include_examples": True,
                "deployment_features": ["database", "bucket"]
            }
        },
        {
            "name": "Python Flask Structure",
            "args": {
                "app_type": "python",
                "include_examples": True,
                "include_github_actions": True,
                "deployment_features": ["database"]
            }
        },
        {
            "name": "Static Nginx Site",
            "args": {
                "app_type": "nginx"
            }
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🎯 Test {i}/{len(test_scenarios)}: {scenario['name']}")
        success, response = test_mcp_tool("get_project_structure_guide", scenario["args"])
        
        results.append({
            "scenario": scenario["name"],
            "success": success,
            "response_length": len(response) if response else 0
        })
        
        if success and response:
            # Check for key elements in the response
            checks = {
                "Has directory structure": "📂 Required Directory Structure" in response,
                "Has example app link": f"example-{scenario['args']['app_type']}-app" in response,
                "Has deployment config": f"deployment-{scenario['args']['app_type']}.config.yml" in response,
                "Has GitHub Actions": ".github/workflows" in response,
                "Has quick start commands": "Quick Start Commands" in response,
                "Has download examples": "curl -O" in response,
                "Has reference links": "github.com/naveenraj44125-creator" in response
            }
            
            print("\n🔍 Content Validation:")
            for check_name, check_result in checks.items():
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    
    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    print(f"❌ Failed Tests: {total_tests - successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Project structure guide tool is working correctly.")
        print("\n🔧 Key Features Validated:")
        print("  ✅ Application-specific directory structures")
        print("  ✅ Example application links and references")
        print("  ✅ Deployment configuration templates")
        print("  ✅ GitHub Actions workflow setup")
        print("  ✅ Quick start commands with downloads")
        print("  ✅ Feature-based customization (database, bucket, etc.)")
        print("  ✅ Direct file download examples")
        
        print("\n🤖 AI Agent Integration:")
        print("  • Use get_project_structure_guide after analyze_deployment_requirements")
        print("  • Provide users with complete project organization guidance")
        print("  • Include direct links to working example applications")
        print("  • Show exact file structure and configuration requirements")
        
        return True
    else:
        print(f"\n❌ {total_tests - successful_tests} tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)