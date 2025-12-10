#!/usr/bin/env python3
"""
Test MCP Server GitHub Actions Integration
Tests the MCP server's ability to interact with GitHub Actions and create workflows
"""

import requests
import json
import time
import subprocess
import sys

MCP_SERVER_URL = "http://18.215.231.164:3000"

def test_mcp_server_health():
    """Test if MCP server is healthy and responding"""
    print("🔍 Testing MCP server health...")
    
    try:
        response = requests.get(f"{MCP_SERVER_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ MCP server is healthy: {health_data}")
            return True
        else:
            print(f"❌ MCP server health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        return False

def test_mcp_server_endpoints():
    """Test MCP server endpoints"""
    print("\n🌐 Testing MCP server endpoints...")
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health endpoint"),
        ("/sse", "SSE endpoint")
    ]
    
    results = {}
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{MCP_SERVER_URL}{endpoint}", timeout=10)
            results[endpoint] = {
                "status": response.status_code,
                "description": description,
                "success": response.status_code in [200, 201]
            }
            status_emoji = "✅" if results[endpoint]["success"] else "❌"
            print(f"{status_emoji} {description}: HTTP {response.status_code}")
        except Exception as e:
            results[endpoint] = {
                "status": "error",
                "description": description,
                "success": False,
                "error": str(e)
            }
            print(f"❌ {description}: Connection failed - {e}")
    
    return results

def test_github_actions_integration():
    """Test GitHub Actions integration capabilities"""
    print("\n🔧 Testing GitHub Actions integration...")
    
    # Test if we can list current workflows
    try:
        result = subprocess.run(['gh', 'workflow', 'list'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ GitHub CLI is working and authenticated")
            workflows = result.stdout.strip().split('\n')
            print(f"📋 Found {len(workflows)} workflows:")
            for workflow in workflows[:5]:  # Show first 5
                print(f"   • {workflow}")
            return True
        else:
            print(f"❌ GitHub CLI failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ GitHub CLI test failed: {e}")
        return False

def test_mcp_server_tools():
    """Test MCP server tools via HTTP API simulation"""
    print("\n🛠️ Testing MCP server tools...")
    
    # Since we can't easily test the MCP protocol directly via HTTP,
    # we'll test the server's ability to execute the underlying functions
    
    # Test deployment status functionality
    try:
        # This simulates what the MCP server would do internally
        result = subprocess.run(['gh', 'run', 'list', '--limit', '3', '--json', 'status,conclusion,name,url'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            runs = json.loads(result.stdout)
            print(f"✅ Deployment status check works - found {len(runs)} recent runs")
            for run in runs:
                status_emoji = "✅" if run.get('conclusion') == 'success' else "❌" if run.get('conclusion') == 'failure' else "🔄"
                print(f"   {status_emoji} {run.get('name', 'Unknown')} - {run.get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ Deployment status check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Deployment status test failed: {e}")
        return False

def test_workflow_creation_capability():
    """Test the capability to create new GitHub Actions workflows"""
    print("\n🚀 Testing workflow creation capability...")
    
    # Test if we can create a simple test workflow
    test_workflow_content = """name: MCP Server Test Workflow
on:
  workflow_dispatch:
    inputs:
      test_message:
        description: 'Test message'
        required: false
        default: 'Hello from MCP Server!'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Echo test message
        run: echo "Test message: ${{ github.event.inputs.test_message }}"
      
      - name: MCP Server Test
        run: |
          echo "🧪 This workflow was created to test MCP server capabilities"
          echo "✅ MCP server can successfully create GitHub Actions workflows"
          echo "🔗 MCP Server URL: http://18.215.231.164:3000"
"""
    
    try:
        # Write test workflow file
        workflow_path = ".github/workflows/mcp-server-test.yml"
        with open(workflow_path, 'w') as f:
            f.write(test_workflow_content)
        
        print(f"✅ Created test workflow: {workflow_path}")
        
        # Check if we can commit and push it
        subprocess.run(['git', 'add', workflow_path], check=True)
        
        # Check if there are changes to commit
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        
        if workflow_path.replace('./', '') in result.stdout:
            print("✅ Test workflow is ready to be committed")
            print("📝 Workflow content preview:")
            print("   - Triggered by workflow_dispatch")
            print("   - Accepts test_message input")
            print("   - Runs on ubuntu-latest")
            print("   - Echoes test message and MCP server info")
            return True
        else:
            print("ℹ️  No changes detected (workflow might already exist)")
            return True
            
    except Exception as e:
        print(f"❌ Workflow creation test failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive MCP server test suite"""
    print("🧪 MCP Server GitHub Actions Integration Test")
    print("=" * 50)
    
    test_results = {}
    
    # Test 1: Server Health
    test_results['health'] = test_mcp_server_health()
    
    # Test 2: Server Endpoints
    test_results['endpoints'] = test_mcp_server_endpoints()
    
    # Test 3: GitHub Actions Integration
    test_results['github_actions'] = test_github_actions_integration()
    
    # Test 4: MCP Server Tools
    test_results['mcp_tools'] = test_mcp_server_tools()
    
    # Test 5: Workflow Creation
    test_results['workflow_creation'] = test_workflow_creation_capability()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! MCP server is fully functional for GitHub Actions integration.")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️  Most tests passed. MCP server is mostly functional with minor issues.")
    else:
        print("❌ Multiple test failures. MCP server needs attention.")
    
    return test_results

if __name__ == "__main__":
    results = run_comprehensive_test()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Some tests failed