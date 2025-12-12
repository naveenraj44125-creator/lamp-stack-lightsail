#!/usr/bin/env python3
"""
Manual test script for Instagram clone
Tests external endpoints without requiring AWS credentials
"""

import requests
import sys

def main():
    ip_address = input("Enter instance IP address [54.208.200.164]: ").strip() or "54.208.200.164"
    
    print(f"\n⚡ Manual Instagram Clone Test")
    print(f"📍 Testing IP: {ip_address}")
    print("=" * 50)
    
    endpoints = [
        ("Main App", f"http://{ip_address}/"),
        ("Health API", f"http://{ip_address}/api/health"),
        ("Status API", f"http://{ip_address}/api/status"),
        ("Posts API", f"http://{ip_address}/api/posts"),
    ]
    
    results = {}
    for name, url in endpoints:
        try:
            print(f"\nTesting {name}: {url}")
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {name}: OK")
                results[name] = 'OK'
                
                # Show response details for APIs
                if 'api' in url:
                    try:
                        data = response.json()
                        print(f"Response: {data}")
                        
                        # Specific checks for status endpoint
                        if 'build_exists' in data:
                            build_status = "✅ EXISTS" if data['build_exists'] else "❌ MISSING"
                            print(f"React Build: {build_status}")
                        if 'build_path' in data:
                            print(f"Build Path: {data['build_path']}")
                    except Exception as e:
                        print(f"Response (text): {response.text[:200]}...")
                else:
                    # For main app, check if it looks like React
                    content = response.text
                    if 'react' in content.lower() or 'instagram' in content.lower():
                        print("✅ Looks like React app")
                    else:
                        print("⚠️  Unexpected content")
                        print(f"Content preview: {content[:100]}...")
                        
            elif response.status_code == 404:
                print(f"❌ {name}: Not Found (404)")
                results[name] = 'Not Found'
            elif response.status_code == 502:
                print(f"❌ {name}: Bad Gateway (502)")
                results[name] = 'Bad Gateway'
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results[name] = f'HTTP {response.status_code}'
                
        except requests.exceptions.ConnectTimeout:
            print(f"❌ {name}: Connection timeout")
            results[name] = 'Timeout'
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Connection refused")
            results[name] = 'Connection refused'
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            results[name] = 'Error'
    
    # Summary
    print(f"\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    working_count = sum(1 for status in results.values() if status == 'OK')
    total_count = len(results)
    
    print(f"Working endpoints: {working_count}/{total_count}")
    
    for name, status in results.items():
        status_icon = "✅" if status == 'OK' else "❌"
        print(f"{status_icon} {name}: {status}")
    
    print(f"\n💡 DIAGNOSIS:")
    
    if working_count == total_count:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print(f"🌐 Instagram Clone is live at: http://{ip_address}/")
        
    elif results.get('Health API') == 'OK' and results.get('Status API') == 'OK':
        print("🖥️  Node.js server is running correctly")
        if results.get('Main App') != 'OK':
            print("⚠️  React build may be missing or not served correctly")
            print("🔧 Solution: Rebuild React app and restart server")
        
    elif any('502' in str(status) for status in results.values()):
        print("🌐 Nginx is running but can't reach Node.js server")
        print("🔧 Solution: Check Node.js server is running on port 3000")
        
    elif any('404' in str(status) for status in results.values()):
        print("🌐 Server is responding but content not found")
        print("🔧 Solution: Check React build exists and server configuration")
        
    elif any('Connection' in str(status) for status in results.values()):
        print("🌐 Cannot connect to server")
        print("🔧 Solution: Check if instance is running and ports are open")
        
    else:
        print("🔍 Mixed issues detected - run comprehensive diagnostics")
    
    print(f"\n🛠️  NEXT STEPS:")
    if working_count < total_count:
        print("1. Run: python3 debug-react-nodejs.py (detailed diagnosis)")
        print("2. Run: python3 fix-react-nodejs.py (automated fix)")
        print("3. Check GitHub Actions logs for deployment errors")
    else:
        print("✅ No action needed - deployment is working correctly!")
    
    return 0 if working_count == total_count else 1

if __name__ == '__main__':
    sys.exit(main())