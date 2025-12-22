#!/usr/bin/env python3
"""
Quick endpoint verification with nginx default page detection
"""

import requests
import sys

def test_endpoint(name, url, expected_content=None):
    """Test a deployment endpoint"""
    print(f"\n🧪 Testing {name}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=15)
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
                return False, "nginx_default"
            elif expected_content and expected_content.lower() in content:
                print(f"✅ {name}: HTTP 200 OK - Expected content found")
                return True, "success"
            elif not expected_content:
                print(f"✅ {name}: HTTP 200 OK - Response received")
                return True, "success"
            else:
                print(f"⚠️  {name}: HTTP 200 OK but expected content '{expected_content}' not found")
                return False, "wrong_content"
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False, "http_error"
            
    except requests.exceptions.Timeout:
        print(f"❌ {name}: Connection timeout")
        return False, "timeout"
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection failed")
        return False, "connection_error"
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False, "error"

def main():
    print("🚀 Quick Endpoint Verification")
    print("=" * 40)
    
    # Test endpoints
    endpoints = [
        ("React Dashboard", "http://35.171.85.222/", "react"),
        ("Python Flask API", "http://18.232.114.213/", "Flask"),
        ("Python Health Endpoint", "http://18.232.114.213/api/health", "healthy"),
        ("Nginx Static Demo", "http://18.215.255.226/", "Welcome to Nginx"),
        ("Node.js Application", "http://3.95.21.139:3000/", "Node.js")
    ]
    
    results = []
    nginx_default_detected = []
    
    for name, url, expected in endpoints:
        success, status = test_endpoint(name, url, expected)
        results.append((name, success, status))
        
        if status == "nginx_default":
            nginx_default_detected.append(name)
    
    print("\n" + "=" * 40)
    print("📊 RESULTS SUMMARY")
    print("=" * 40)
    
    working_count = 0
    for name, success, status in results:
        if success:
            print(f"✅ {name}: WORKING")
            working_count += 1
        else:
            status_msg = {
                "nginx_default": "NGINX DEFAULT PAGE",
                "wrong_content": "WRONG CONTENT",
                "http_error": "HTTP ERROR",
                "timeout": "TIMEOUT",
                "connection_error": "CONNECTION ERROR",
                "error": "ERROR"
            }.get(status, "FAILED")
            print(f"❌ {name}: {status_msg}")
    
    print(f"\n📈 {working_count}/{len(endpoints)} endpoints working correctly")
    
    if nginx_default_detected:
        print(f"\n⚠️  NGINX DEFAULT PAGE DETECTED ON:")
        for name in nginx_default_detected:
            print(f"   - {name}")
        print("\n💡 These deployments need nginx configuration fixes.")
        print("   The application files are deployed but nginx is serving the default page.")
        print("   Use the troubleshooting tools or manual fixes to resolve this.")
    
    return 0 if working_count == len(endpoints) else 1

if __name__ == '__main__':
    sys.exit(main())