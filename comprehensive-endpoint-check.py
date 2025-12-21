#!/usr/bin/env python3
"""
Comprehensive endpoint verification for all 8 deployments
"""

import requests
import boto3
import sys
import time
from typing import Dict, Tuple, Optional

def get_instance_ip(instance_name: str) -> Optional[str]:
    """Get the public IP of a Lightsail instance"""
    try:
        client = boto3.client('lightsail', region_name='us-east-1')
        response = client.get_instance(instanceName=instance_name)
        return response['instance']['publicIpAddress']
    except Exception as e:
        print(f"❌ Error getting IP for {instance_name}: {str(e)}")
        return None

def test_endpoint(name: str, url: str, expected_content: str = None, timeout: int = 15) -> Tuple[bool, str, str]:
    """Test a deployment endpoint"""
    print(f"\n🧪 Testing {name}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=timeout)
        content = response.text.lower()
        
        if response.status_code == 200:
            # Check for nginx default page indicators
            nginx_default_indicators = [
                "welcome to nginx",
                "nginx.*default",
                "test page for the nginx",
                "nginx http server",
                "default nginx page"
            ]
            
            is_nginx_default = any(indicator in content for indicator in nginx_default_indicators)
            
            if is_nginx_default:
                print("⚠️  NGINX DEFAULT PAGE DETECTED - Application not properly configured!")
                return False, "nginx_default", content[:200]
            elif expected_content and expected_content.lower() in content:
                print(f"✅ {name}: HTTP 200 OK - Expected content found")
                return True, "success", content[:200]
            elif not expected_content:
                print(f"✅ {name}: HTTP 200 OK - Response received")
                return True, "success", content[:200]
            else:
                print(f"⚠️  {name}: HTTP 200 OK but expected content '{expected_content}' not found")
                return False, "wrong_content", content[:200]
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False, f"http_{response.status_code}", ""
            
    except requests.exceptions.Timeout:
        print(f"❌ {name}: Connection timeout")
        return False, "timeout", ""
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection failed")
        return False, "connection_error", ""
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False, "error", ""

def main():
    print("🚀 Comprehensive Endpoint Verification - All 8 Deployments")
    print("=" * 60)
    
    # All deployment configurations with instance names
    deployments = [
        {
            "name": "React Dashboard",
            "instance": "react-dashboard-v6",
            "expected": "react",
            "port": 80
        },
        {
            "name": "Python Flask API",
            "instance": "python-flask-api-v6", 
            "expected": "Flask",
            "port": 80
        },
        {
            "name": "Nginx Static Demo",
            "instance": "nginx-static-demo-v6",
            "expected": "Welcome to Nginx",
            "port": 80
        },
        {
            "name": "Node.js Application",
            "instance": "simple-blog-1766109629",
            "expected": "Node.js",
            "port": 3000
        },
        {
            "name": "LAMP Stack Demo",
            "instance": "amazon-linux-test-v6",
            "expected": "LAMP",
            "port": 80
        },
        {
            "name": "Docker LAMP Demo",
            "instance": "docker-lamp-demo-v6",
            "expected": "Docker",
            "port": 80
        },
        {
            "name": "Recipe Manager Docker",
            "instance": "recipe-manager-docker-v6",
            "expected": "Recipe",
            "port": 80
        },
        {
            "name": "Social Media App",
            "instance": "social-media-app-instance-1",
            "expected": "Social",
            "port": 80
        }
    ]
    
    print("📡 Getting instance IPs from AWS Lightsail...")
    
    # Get IPs for all instances
    for deployment in deployments:
        ip = get_instance_ip(deployment["instance"])
        if ip:
            port = deployment["port"]
            if port == 80:
                deployment["url"] = f"http://{ip}/"
            else:
                deployment["url"] = f"http://{ip}:{port}/"
            deployment["ip"] = ip
            print(f"✅ {deployment['name']}: {deployment['url']}")
        else:
            deployment["url"] = None
            deployment["ip"] = None
            print(f"❌ {deployment['name']}: Could not get IP")
    
    print("\n" + "=" * 60)
    print("🔍 TESTING ALL ENDPOINTS")
    print("=" * 60)
    
    results = []
    working_count = 0
    nginx_default_detected = []
    
    for deployment in deployments:
        if deployment["url"]:
            success, status, content = test_endpoint(
                deployment["name"], 
                deployment["url"], 
                deployment["expected"]
            )
            results.append((deployment["name"], success, status, deployment["url"]))
            
            if success:
                working_count += 1
            elif status == "nginx_default":
                nginx_default_detected.append(deployment["name"])
        else:
            results.append((deployment["name"], False, "no_ip", "N/A"))
    
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE RESULTS SUMMARY")
    print("=" * 60)
    
    for name, success, status, url in results:
        if success:
            print(f"✅ {name}: WORKING")
            print(f"   URL: {url}")
        else:
            status_msg = {
                "nginx_default": "NGINX DEFAULT PAGE",
                "wrong_content": "WRONG CONTENT", 
                "timeout": "TIMEOUT",
                "connection_error": "CONNECTION ERROR",
                "no_ip": "NO IP ADDRESS",
                "error": "ERROR"
            }.get(status, status.upper())
            print(f"❌ {name}: {status_msg}")
            print(f"   URL: {url}")
    
    print(f"\n📈 OVERALL STATUS: {working_count}/{len(deployments)} endpoints working correctly")
    
    if nginx_default_detected:
        print(f"\n⚠️  NGINX DEFAULT PAGE DETECTED ON:")
        for name in nginx_default_detected:
            print(f"   - {name}")
        print("\n💡 These deployments need nginx configuration fixes.")
        print("   The application files are deployed but nginx is serving the default page.")
    
    # Additional health checks
    print(f"\n🔍 ADDITIONAL HEALTH CHECKS")
    print("=" * 30)
    
    # Test Python health endpoint specifically
    python_deployment = next((d for d in deployments if d["name"] == "Python Flask API"), None)
    if python_deployment and python_deployment.get("ip"):
        health_url = f"http://{python_deployment['ip']}/api/health"
        success, status, content = test_endpoint("Python Health Endpoint", health_url, "healthy")
        if success:
            print("✅ Python Flask API health endpoint working")
        else:
            print("❌ Python Flask API health endpoint failed")
    
    # Summary recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("=" * 20)
    
    if working_count == len(deployments):
        print("🎉 ALL DEPLOYMENTS ARE FULLY FUNCTIONAL!")
        print("✅ GitHub Actions should work without issues")
    else:
        failed_count = len(deployments) - working_count
        print(f"⚠️  {failed_count} deployment(s) need attention:")
        
        if nginx_default_detected:
            print("   • Fix nginx default page issues using the nginx configurator")
        
        timeout_issues = [name for name, success, status, url in results if status == "timeout"]
        if timeout_issues:
            print("   • Check service status for timeout issues:")
            for name in timeout_issues:
                print(f"     - {name}")
        
        connection_issues = [name for name, success, status, url in results if status == "connection_error"]
        if connection_issues:
            print("   • Check firewall and service configuration for connection issues:")
            for name in connection_issues:
                print(f"     - {name}")
    
    return 0 if working_count == len(deployments) else 1

if __name__ == '__main__':
    # Source AWS credentials
    try:
        import subprocess
        subprocess.run(["source", ".aws-creds.sh"], shell=True, check=False)
    except:
        pass
    
    sys.exit(main())