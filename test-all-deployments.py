#!/usr/bin/env python3
"""
Test all deployments to confirm everything is working
"""

import requests
import sys

def test_deployment(name, url, expected_content=None):
    """Test a deployment and return status"""
    print(f"\n🧪 Testing {name}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {name}: HTTP 200 OK")
            if expected_content and expected_content.lower() in response.text.lower():
                print(f"✅ {name}: Expected content found")
                return True
            elif not expected_content:
                print(f"✅ {name}: Response received")
                return True
            else:
                print(f"⚠️ {name}: Expected content not found")
                return False
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: Connection failed - {str(e)}")
        return False

def main():
    print("🚀 Testing All Deployments")
    print("=" * 50)
    
    deployments = [
        {
            "name": "React Dashboard",
            "url": "http://35.171.85.222/",
            "expected": "react"
        },
        {
            "name": "Nginx Static Demo", 
            "url": "http://18.215.255.226/",
            "expected": "html"
        },
        {
            "name": "Python Flask API",
            "url": "http://18.232.114.213/",
            "expected": "html"
        },
        {
            "name": "Python Health Endpoint",
            "url": "http://18.232.114.213/api/health",
            "expected": "healthy"
        }
    ]
    
    results = []
    for deployment in deployments:
        success = test_deployment(
            deployment["name"], 
            deployment["url"], 
            deployment.get("expected")
        )
        results.append((deployment["name"], success))
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    
    all_working = True
    for name, success in results:
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{name}: {status}")
        if not success:
            all_working = False
    
    print("\n" + "=" * 50)
    if all_working:
        print("🎉 ALL DEPLOYMENTS ARE FULLY FUNCTIONAL!")
        print("✅ GitHub Actions should now work without issues")
    else:
        print("⚠️ Some deployments still have issues")
    print("=" * 50)
    
    return 0 if all_working else 1

if __name__ == '__main__':
    sys.exit(main())