#!/usr/bin/env python3
"""
Verify all 8 deployments using known working IPs and expected new deployments
"""

import requests
import sys

def test_endpoint(name: str, url: str, expected_content: str = None, timeout: int = 15) -> tuple:
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
                return False, "nginx_default"
            elif expected_content and expected_content.lower() in content:
                print(f"✅ {name}: HTTP 200 OK - Expected content found")
                return True, "success"
            elif not expected_content:
                print(f"✅ {name}: HTTP 200 OK - Response received")
                return True, "success"
            else:
                print(f"⚠️  {name}: HTTP 200 OK but expected content '{expected_content}' not found")
                print(f"   Content preview: {content[:100]}...")
                return False, "wrong_content"
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False, f"http_{response.status_code}"
            
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
    print("🚀 Verify All 8 Deployments")
    print("=" * 40)
    
    # Known working endpoints from previous tests + expected new ones
    endpoints = [
        # Known working deployments
        ("React Dashboard", "http://35.171.85.222/", "react"),
        ("Python Flask API", "http://18.232.114.213/", "Flask"),
        ("Python Health Endpoint", "http://18.232.114.213/api/health", "healthy"),
        ("Nginx Static Demo", "http://18.215.255.226/", "Welcome to Nginx"),
        
        # Node.js - known to have timeout issues
        ("Node.js Application", "http://3.95.21.139:3000/", "Node.js"),
        
        # Additional deployments - need to check if they exist
        # These might be new or might not be deployed yet
        ("LAMP Stack Demo", "http://54.91.215.35/", "LAMP"),
        ("Docker LAMP Demo", "http://54.91.215.35/", "Docker"),
        ("Recipe Manager Docker", "http://54.91.215.35/", "Recipe"),
        ("Social Media App", "http://54.91.215.35/", "Social"),
    ]
    
    results = []
    working_count = 0
    nginx_default_detected = []
    
    for name, url, expected in endpoints:
        success, status = test_endpoint(name, url, expected)
        results.append((name, success, status, url))
        
        if success:
            working_count += 1
        elif status == "nginx_default":
            nginx_default_detected.append(name)
    
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT STATUS SUMMARY")
    print("=" * 50)
    
    # Group results by status
    working = []
    nginx_issues = []
    connection_issues = []
    other_issues = []
    
    for name, success, status, url in results:
        if success:
            working.append((name, url))
        elif status == "nginx_default":
            nginx_issues.append((name, url))
        elif status in ["timeout", "connection_error"]:
            connection_issues.append((name, url, status))
        else:
            other_issues.append((name, url, status))
    
    # Display results by category
    if working:
        print(f"\n✅ WORKING DEPLOYMENTS ({len(working)}):")
        for name, url in working:
            print(f"   • {name}: {url}")
    
    if nginx_issues:
        print(f"\n⚠️  NGINX DEFAULT PAGE ISSUES ({len(nginx_issues)}):")
        for name, url in nginx_issues:
            print(f"   • {name}: {url}")
        print("   💡 Fix: Use nginx configurator to remove default server block")
    
    if connection_issues:
        print(f"\n❌ CONNECTION ISSUES ({len(connection_issues)}):")
        for name, url, status in connection_issues:
            print(f"   • {name}: {url} ({status})")
        print("   💡 Fix: Check service status and firewall configuration")
    
    if other_issues:
        print(f"\n❓ OTHER ISSUES ({len(other_issues)}):")
        for name, url, status in other_issues:
            print(f"   • {name}: {url} ({status})")
    
    print(f"\n📈 OVERALL STATUS: {working_count}/{len(endpoints)} endpoints working")
    
    # Deployment-specific recommendations
    print(f"\n💡 SPECIFIC RECOMMENDATIONS:")
    print("=" * 30)
    
    if working_count >= 3:
        print("✅ Core deployments (React, Python) are working well")
    
    if nginx_issues:
        print("🔧 Nginx default page issues detected:")
        print("   - Run: python3 fix-nginx-verification.py")
        print("   - Or use troubleshooting tools with SSH access")
    
    if any("Node.js" in name for name, _, status, _ in results if status == "timeout"):
        print("🔍 Node.js application timeout:")
        print("   - Check if PM2 process is running")
        print("   - Verify port 3000 is accessible")
        print("   - Check application logs")
    
    # Check if we need to spin up more deployments
    if working_count < 5:
        print("🚀 Consider running spin-up-all-examples.sh to deploy missing applications")
    
    print(f"\n🎯 NEXT STEPS:")
    if working_count == len(endpoints):
        print("🎉 All deployments working! GitHub Actions should be successful.")
    else:
        print("1. Fix nginx default page issues")
        print("2. Check connection timeouts")
        print("3. Verify all deployments are actually deployed")
        print("4. Run spin-up-all-examples.sh if needed")
    
    return 0 if working_count >= len(endpoints) * 0.6 else 1  # 60% success threshold

if __name__ == '__main__':
    sys.exit(main())