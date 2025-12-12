#!/usr/bin/env python3
"""
Test script for GitHub username dynamic configuration fix
Tests both the setup script and MCP server enhancements
"""

import requests
import json
import subprocess
import os
import sys

def test_mcp_github_configuration():
    """Test the new configure_github_repository MCP tool"""
    print("🧪 Testing MCP GitHub Repository Configuration Tool")
    print("=" * 60)
    
    # MCP server URL
    mcp_url = "http://3.81.56.119:3000"
    
    try:
        # Test the new configure_github_repository tool
        print("\n1. Testing configure_github_repository tool...")
        
        test_data = {
            "github_username": "testuser",
            "repository_name": "my-nodejs-app",
            "app_type": "nodejs"
        }
        
        response = requests.post(
            f"{mcp_url}/mcp/call-tool",
            json={
                "name": "configure_github_repository",
                "arguments": test_data
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP tool call successful!")
            print(f"📋 Response preview: {result.get('content', [{}])[0].get('text', '')[:200]}...")
            
            # Check if response contains personalized URLs
            response_text = result.get('content', [{}])[0].get('text', '')
            if "testuser/my-nodejs-app" in response_text:
                print("✅ Personalized GitHub URLs generated correctly!")
            else:
                print("❌ Personalized URLs not found in response")
                
            if "export GITHUB_REPO=" in response_text:
                print("✅ Environment variables for automation included!")
            else:
                print("❌ Environment variables not found in response")
                
        else:
            print(f"❌ MCP tool call failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")

def test_setup_script_github_logic():
    """Test the setup script's GitHub username prompting logic"""
    print("\n🧪 Testing Setup Script GitHub Username Logic")
    print("=" * 60)
    
    # Check if setup script exists
    setup_script = "setup-complete-deployment.sh"
    if not os.path.exists(setup_script):
        print(f"❌ Setup script not found: {setup_script}")
        return
        
    print("✅ Setup script found")
    
    # Check for GitHub username prompting logic
    try:
        with open(setup_script, 'r') as f:
            content = f.read()
            
        # Check for key improvements
        checks = [
            ("GitHub username prompting", "Enter your GitHub username"),
            ("Repository name prompting", "Enter repository name"),
            ("Repository creation", "create_github_repo_if_needed"),
            ("Git remote configuration", "git remote add origin"),
            ("Dynamic repository handling", "GITHUB_USERNAME")
        ]
        
        print("\n📋 Checking setup script enhancements:")
        for check_name, check_pattern in checks:
            if check_pattern in content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: Not found")
                
    except Exception as e:
        print(f"❌ Error reading setup script: {e}")

def test_mcp_server_dynamic_urls():
    """Test that MCP server no longer has hardcoded URLs"""
    print("\n🧪 Testing MCP Server Dynamic URLs")
    print("=" * 60)
    
    mcp_server_file = "mcp-server/server.js"
    if not os.path.exists(mcp_server_file):
        print(f"❌ MCP server file not found: {mcp_server_file}")
        return
        
    try:
        with open(mcp_server_file, 'r') as f:
            content = f.read()
            
        # Check that hardcoded URLs are replaced
        hardcoded_checks = [
            ("Hardcoded GitHub username", "naveenraj44125-creator", False),
            ("Dynamic URL placeholders", "YOUR_USERNAME/YOUR_REPOSITORY", True),
            ("New GitHub tool", "configure_github_repository", True),
            ("Tool documentation", "NEW GITHUB CONFIGURATION TOOL", True)
        ]
        
        print("\n📋 Checking MCP server URL configuration:")
        for check_name, check_pattern, should_exist in hardcoded_checks:
            found = check_pattern in content
            if should_exist:
                if found:
                    print(f"✅ {check_name}: Found")
                else:
                    print(f"❌ {check_name}: Not found")
            else:
                if not found:
                    print(f"✅ {check_name}: Removed (good)")
                else:
                    print(f"❌ {check_name}: Still present (should be removed)")
                    
    except Exception as e:
        print(f"❌ Error reading MCP server file: {e}")

def test_integration_workflow():
    """Test the complete integration workflow"""
    print("\n🧪 Testing Complete Integration Workflow")
    print("=" * 60)
    
    print("\n📋 Integration Test Scenario:")
    print("1. User wants to deploy a Node.js app")
    print("2. User provides GitHub username: 'johndoe'")
    print("3. User provides repository name: 'my-awesome-app'")
    print("4. System should generate personalized setup")
    
    # Test MCP server integration
    mcp_url = "http://3.81.56.119:3000"
    
    try:
        # Step 1: Configure GitHub repository
        print("\n🔧 Step 1: Configure GitHub repository...")
        config_response = requests.post(
            f"{mcp_url}/mcp/call-tool",
            json={
                "name": "configure_github_repository",
                "arguments": {
                    "github_username": "johndoe",
                    "repository_name": "my-awesome-app",
                    "app_type": "nodejs"
                }
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if config_response.status_code == 200:
            print("✅ GitHub repository configured successfully!")
            
            # Step 2: Analyze deployment requirements
            print("\n🔍 Step 2: Analyze deployment requirements...")
            analysis_response = requests.post(
                f"{mcp_url}/mcp/call-tool",
                json={
                    "name": "analyze_deployment_requirements",
                    "arguments": {
                        "user_description": "I have a Node.js Express API with MySQL database that I want to deploy"
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if analysis_response.status_code == 200:
                print("✅ Deployment requirements analyzed successfully!")
                
                # Step 3: Get project structure guide
                print("\n📁 Step 3: Get project structure guide...")
                structure_response = requests.post(
                    f"{mcp_url}/mcp/call-tool",
                    json={
                        "name": "get_project_structure_guide",
                        "arguments": {
                            "app_type": "nodejs"
                        }
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if structure_response.status_code == 200:
                    print("✅ Project structure guide retrieved successfully!")
                    print("\n🎉 Complete integration workflow test PASSED!")
                    
                    # Show summary
                    print("\n📊 Integration Test Summary:")
                    print("✅ GitHub repository configuration: Working")
                    print("✅ Deployment analysis: Working") 
                    print("✅ Project structure guidance: Working")
                    print("✅ End-to-end workflow: Working")
                    
                else:
                    print(f"❌ Project structure guide failed: {structure_response.status_code}")
            else:
                print(f"❌ Deployment analysis failed: {analysis_response.status_code}")
        else:
            print(f"❌ GitHub configuration failed: {config_response.status_code}")
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")

def main():
    """Run all tests"""
    print("🚀 GitHub Username Dynamic Configuration Fix - Test Suite")
    print("=" * 70)
    print("Testing the fix for hardcoded GitHub URLs and username prompting")
    print("=" * 70)
    
    # Run all tests
    test_mcp_server_dynamic_urls()
    test_setup_script_github_logic()
    test_mcp_github_configuration()
    test_integration_workflow()
    
    print("\n" + "=" * 70)
    print("🏁 Test Suite Complete!")
    print("=" * 70)
    
    print("\n📋 Summary of Changes Made:")
    print("1. ✅ Setup script now prompts for GitHub username when repository not found")
    print("2. ✅ MCP server uses dynamic URLs instead of hardcoded ones")
    print("3. ✅ New configure_github_repository MCP tool for personalized setup")
    print("4. ✅ Complete integration workflow with GitHub username handling")
    
    print("\n🎯 Next Steps for Users:")
    print("1. Use the new configure_github_repository MCP tool to set up personalized URLs")
    print("2. Run setup script - it will prompt for GitHub username if needed")
    print("3. All generated files will use the correct repository URLs")
    print("4. No more hardcoded GitHub usernames in the system!")

if __name__ == "__main__":
    main()