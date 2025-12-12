#!/usr/bin/env python3

"""
Test Enhanced MCP Server with Configurable IAM Role
Tests the new aws_role_arn parameter and command output functionality
"""

import json
import requests
import time
import sys

def test_mcp_server():
    """Test the enhanced MCP server with configurable IAM role"""
    
    # MCP server URL (adjust if different)
    base_url = "http://3.81.56.119:3000"
    
    print("🧪 Testing Enhanced MCP Server with Configurable IAM Role")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Setup with custom IAM role ARN
    print("\n2️⃣ Testing setup_complete_deployment with custom IAM role...")
    
    test_params = {
        "mode": "fully_automated",
        "app_type": "nodejs",
        "app_name": "test-nodejs-app",
        "instance_name": "nodejs-test-instance",
        "aws_region": "us-east-1",
        "aws_role_arn": "arn:aws:iam::123456789012:role/MyCustomGitHubActionsRole",
        "app_version": "1.0.0",
        "blueprint_id": "ubuntu_22_04",
        "bundle_id": "small_3_0",
        "database_type": "postgresql",
        "db_external": False,
        "db_name": "test_app_db",
        "enable_bucket": True,
        "bucket_name": "nodejs-test-bucket-12345",
        "bucket_access": "read_write",
        "bucket_bundle": "small_1_0",
        "github_repo": "test-nodejs-deployment",
        "repo_visibility": "private"
    }
    
    try:
        # Create SSE connection
        sse_response = requests.get(f"{base_url}/sse", stream=True, timeout=30)
        
        if sse_response.status_code != 200:
            print(f"❌ SSE connection failed: {sse_response.status_code}")
            return False
        
        print("✅ SSE connection established")
        
        # Extract session ID from SSE response
        session_id = None
        for line in sse_response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if 'sessionId' in data:
                        session_id = data['sessionId']
                        break
                except:
                    continue
        
        if not session_id:
            print("❌ Could not extract session ID")
            return False
        
        print(f"✅ Session ID: {session_id}")
        
        # Send MCP message
        message_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": test_params
            }
        }
        
        message_response = requests.post(
            f"{base_url}/message?sessionId={session_id}",
            json=message_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if message_response.status_code == 200:
            result = message_response.json()
            print("✅ MCP call successful")
            
            # Check if result contains content
            if 'result' in result and 'content' in result['result']:
                content = result['result']['content'][0]['text']
                
                # Verify custom IAM role ARN is included
                if "arn:aws:iam::123456789012:role/MyCustomGitHubActionsRole" in content:
                    print("✅ Custom IAM role ARN found in output")
                else:
                    print("❌ Custom IAM role ARN not found in output")
                    return False
                
                # Verify environment variables are set
                if "AWS_ROLE_ARN=" in content:
                    print("✅ AWS_ROLE_ARN environment variable found")
                else:
                    print("❌ AWS_ROLE_ARN environment variable not found")
                    return False
                
                # Verify command format
                if "curl -O" in content and "chmod +x" in content:
                    print("✅ Direct executable commands found")
                else:
                    print("❌ Direct executable commands not found")
                    return False
                
                # Show sample of output
                print("\n📋 Sample Output:")
                print("-" * 40)
                lines = content.split('\n')[:20]  # First 20 lines
                for line in lines:
                    print(line)
                print("...")
                print("-" * 40)
                
            else:
                print("❌ No content in MCP response")
                return False
                
        else:
            print(f"❌ MCP call failed: {message_response.status_code}")
            print(f"Response: {message_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ MCP test error: {e}")
        return False
    
    # Test 3: Setup without custom IAM role (default behavior)
    print("\n3️⃣ Testing setup_complete_deployment with default IAM role...")
    
    default_params = {
        "mode": "fully_automated",
        "app_type": "lamp",
        "app_name": "test-lamp-app",
        "instance_name": "lamp-test-instance",
        "aws_region": "us-west-2",
        # No aws_role_arn parameter - should use default
        "database_type": "mysql",
        "enable_bucket": False,
        "github_repo": "test-lamp-deployment"
    }
    
    try:
        # Create new SSE connection
        sse_response = requests.get(f"{base_url}/sse", stream=True, timeout=30)
        
        # Extract session ID
        session_id = None
        for line in sse_response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if 'sessionId' in data:
                        session_id = data['sessionId']
                        break
                except:
                    continue
        
        # Send MCP message
        message_data = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": default_params
            }
        }
        
        message_response = requests.post(
            f"{base_url}/message?sessionId={session_id}",
            json=message_data,
            timeout=30
        )
        
        if message_response.status_code == 200:
            result = message_response.json()
            content = result['result']['content'][0]['text']
            
            # Verify default IAM role naming is mentioned
            if "GitHubActions-lamp-deployment" in content:
                print("✅ Default IAM role naming found")
            else:
                print("❌ Default IAM role naming not found")
                return False
            
            # Verify AWS_ROLE_ARN is NOT in environment variables (since not provided)
            env_lines = [line for line in content.split('\n') if 'export AWS_ROLE_ARN=' in line]
            if not env_lines:
                print("✅ AWS_ROLE_ARN correctly omitted when not provided")
            else:
                print("❌ AWS_ROLE_ARN should not be set when not provided")
                return False
                
        else:
            print(f"❌ Default IAM role test failed: {message_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Default IAM role test error: {e}")
        return False
    
    # Test 4: Invalid IAM role ARN format
    print("\n4️⃣ Testing invalid IAM role ARN format...")
    
    invalid_params = {
        "mode": "fully_automated",
        "app_type": "nodejs",
        "app_name": "test-app",
        "instance_name": "test-instance",
        "aws_role_arn": "invalid-arn-format"  # Invalid format
    }
    
    try:
        # Create new SSE connection
        sse_response = requests.get(f"{base_url}/sse", stream=True, timeout=30)
        
        # Extract session ID
        session_id = None
        for line in sse_response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if 'sessionId' in data:
                        session_id = data['sessionId']
                        break
                except:
                    continue
        
        # Send MCP message
        message_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "setup_complete_deployment",
                "arguments": invalid_params
            }
        }
        
        message_response = requests.post(
            f"{base_url}/message?sessionId={session_id}",
            json=message_data,
            timeout=30
        )
        
        if message_response.status_code == 200:
            result = message_response.json()
            content = result['result']['content'][0]['text']
            
            # Should contain error message about invalid ARN format
            if "Invalid AWS IAM role ARN format" in content:
                print("✅ Invalid ARN format correctly rejected")
            else:
                print("❌ Invalid ARN format should be rejected")
                return False
                
        else:
            print(f"❌ Invalid ARN test failed: {message_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid ARN test error: {e}")
        return False
    
    print("\n🎉 All tests passed! Enhanced MCP server is working correctly.")
    print("\n✅ Key Features Verified:")
    print("  - Custom IAM role ARN parameter support")
    print("  - Environment variable generation with custom role")
    print("  - Default IAM role naming when no custom role provided")
    print("  - IAM role ARN format validation")
    print("  - Direct executable command output")
    
    return True

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)