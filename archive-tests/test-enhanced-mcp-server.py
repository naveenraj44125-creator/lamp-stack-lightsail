#!/usr/bin/env python3

"""
Enhanced MCP Server Test Suite
Tests the updated Lightsail Deployment MCP server with new setup script integration.
"""

import json
import requests
import time
import sys
from typing import Dict, Any, List

class MCPServerTester:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session_id = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_health_check(self) -> bool:
        """Test server health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "service", "version"]
                if all(field in data for field in expected_fields):
                    self.log_test("Health Check", True, f"Service: {data.get('service')}, Version: {data.get('version')}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Missing fields in response: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_sse_connection(self) -> bool:
        """Test SSE endpoint connection"""
        try:
            response = requests.get(f"{self.base_url}/sse", timeout=5, stream=True)
            if response.status_code == 200:
                # Check for SSE headers
                content_type = response.headers.get('content-type', '')
                if 'text/event-stream' in content_type:
                    self.log_test("SSE Connection", True, "SSE endpoint accessible")
                    return True
                else:
                    self.log_test("SSE Connection", False, f"Wrong content type: {content_type}")
                    return False
            else:
                self.log_test("SSE Connection", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("SSE Connection", False, f"Connection error: {str(e)}")
            return False
    
    def test_mcp_tools_list(self) -> bool:
        """Test MCP tools listing"""
        try:
            # This is a simplified test - in real MCP, you'd use the proper protocol
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Check for expected tool names in the HTML
                expected_tools = [
                    "setup_complete_deployment",
                    "get_deployment_examples", 
                    "get_deployment_status",
                    "diagnose_deployment"
                ]
                
                found_tools = []
                for tool in expected_tools:
                    if tool in content:
                        found_tools.append(tool)
                
                if len(found_tools) == len(expected_tools):
                    self.log_test("MCP Tools List", True, f"All {len(expected_tools)} tools found")
                    return True
                else:
                    missing = set(expected_tools) - set(found_tools)
                    self.log_test("MCP Tools List", False, f"Missing tools: {missing}")
                    return False
            else:
                self.log_test("MCP Tools List", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("MCP Tools List", False, f"Error: {str(e)}")
            return False
    
    def test_tool_descriptions(self) -> bool:
        """Test that tool descriptions mention key features"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Check for key features mentioned in descriptions
                key_features = [
                    "6 app types",  # Updated from "All Application Types"
                    "LAMP, Node.js, Python, React, Docker, Nginx",
                    "database support",
                    "GitHub OIDC",
                    "bucket integration"
                ]
                
                found_features = []
                for feature in key_features:
                    if feature.lower() in content.lower():
                        found_features.append(feature)
                
                if len(found_features) >= 3:  # At least 3 key features should be mentioned
                    self.log_test("Tool Descriptions", True, f"Found {len(found_features)}/{len(key_features)} key features")
                    return True
                else:
                    self.log_test("Tool Descriptions", False, f"Only found {len(found_features)} key features: {found_features}")
                    return False
            else:
                self.log_test("Tool Descriptions", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Tool Descriptions", False, f"Error: {str(e)}")
            return False
    
    def test_setup_script_features(self) -> bool:
        """Test that setup script features are properly documented"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for setup script specific features
                setup_features = [
                    "interactive mode",
                    "auto mode", 
                    "help mode",
                    "deployment configuration",
                    "github actions workflow",
                    "example application"
                ]
                
                found_features = []
                for feature in setup_features:
                    if feature in content:
                        found_features.append(feature)
                
                if len(found_features) >= 4:
                    self.log_test("Setup Script Features", True, f"Found {len(found_features)}/{len(setup_features)} features")
                    return True
                else:
                    self.log_test("Setup Script Features", False, f"Only found {len(found_features)} features: {found_features}")
                    return False
            else:
                self.log_test("Setup Script Features", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Setup Script Features", False, f"Error: {str(e)}")
            return False
    
    def test_client_side_execution(self) -> bool:
        """Test that documentation emphasizes client-side execution"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for client-side execution indicators
                client_indicators = [
                    "local machine",
                    "your machine", 
                    "client",
                    "download",
                    "curl",
                    "not on the mcp server",
                    "does not install"
                ]
                
                found_indicators = []
                for indicator in client_indicators:
                    if indicator in content:
                        found_indicators.append(indicator)
                
                if len(found_indicators) >= 3:
                    self.log_test("Client-Side Execution", True, f"Found {len(found_indicators)} client-side indicators")
                    return True
                else:
                    self.log_test("Client-Side Execution", False, f"Only found {len(found_indicators)} indicators: {found_indicators}")
                    return False
            else:
                self.log_test("Client-Side Execution", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Client-Side Execution", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🧪 Testing Enhanced MCP Server")
        print("=" * 50)
        
        tests = [
            self.test_health_check,
            self.test_sse_connection,
            self.test_mcp_tools_list,
            self.test_tool_descriptions,
            self.test_setup_script_features,
            self.test_client_side_execution
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(0.5)  # Brief pause between tests
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! MCP server is working correctly.")
            success = True
        else:
            print(f"⚠️  {total - passed} test(s) failed. Check the details above.")
            success = False
        
        return {
            "success": success,
            "passed": passed,
            "total": total,
            "results": self.test_results
        }

def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Enhanced MCP Server")
    parser.add_argument("--url", default="http://localhost:3000", 
                       help="MCP server URL (default: http://localhost:3000)")
    parser.add_argument("--json", action="store_true", 
                       help="Output results in JSON format")
    
    args = parser.parse_args()
    
    tester = MCPServerTester(args.url)
    results = tester.run_all_tests()
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()