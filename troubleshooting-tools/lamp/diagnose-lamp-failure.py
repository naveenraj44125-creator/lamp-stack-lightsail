#!/usr/bin/env python3
"""
Diagnose LAMP Stack failure on Amazon Linux
This script analyzes the most likely causes of Apache (httpd) not starting
"""

import requests
import subprocess
import sys
import time

def test_endpoint(url, timeout=10):
    """Test if an endpoint is accessible"""
    try:
        response = requests.get(url, timeout=timeout)
        return True, response.status_code, response.text[:200]
    except requests.exceptions.ConnectionError:
        return False, "connection_refused", "Connection refused - service not running"
    except requests.exceptions.Timeout:
        return False, "timeout", "Connection timeout"
    except Exception as e:
        return False, "error", str(e)

def check_port(host, port):
    """Check if a port is open using nmap"""
    try:
        result = subprocess.run(f"nmap -p {port} {host}", shell=True, capture_output=True, text=True, timeout=30)
        return "open" in result.stdout
    except:
        return False

def main():
    print("🔍 LAMP Stack Failure Diagnosis")
    print("=" * 40)
    print("Instance: amazon-linux-test-v7-20241220")
    print("IP: 54.175.20.108")
    print("Expected: Apache (httpd) serving LAMP application")
    print("=" * 40)
    
    # Test 1: Basic connectivity
    print("\n1️⃣  Testing basic connectivity...")
    try:
        result = subprocess.run("ping -c 3 54.175.20.108", shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ Instance is reachable (ping successful)")
        else:
            print("❌ Instance is not reachable (ping failed)")
            return 1
    except:
        print("❌ Ping test failed")
        return 1
    
    # Test 2: Port scan
    print("\n2️⃣  Testing port accessibility...")
    ports_to_check = [22, 80, 443, 8080]
    open_ports = []
    
    for port in ports_to_check:
        if check_port("54.175.20.108", port):
            open_ports.append(port)
            print(f"✅ Port {port} is open")
        else:
            print(f"❌ Port {port} is closed")
    
    # Test 3: HTTP endpoint test
    print("\n3️⃣  Testing HTTP endpoint...")
    success, status, content = test_endpoint("http://54.175.20.108/")
    
    if success:
        print(f"✅ HTTP endpoint accessible (status: {status})")
        print(f"   Content preview: {content}")
    else:
        print(f"❌ HTTP endpoint failed: {status}")
        print(f"   Details: {content}")
    
    # Analysis
    print("\n📊 DIAGNOSIS RESULTS:")
    print("=" * 30)
    
    if 22 in open_ports:
        print("✅ SSH (port 22) is open - instance is running")
    else:
        print("❌ SSH (port 22) is closed - instance may be down")
        return 1
    
    if 80 not in open_ports:
        print("❌ HTTP (port 80) is closed - web server not running")
        print("\n🔍 LIKELY CAUSES:")
        print("   1. Apache (httpd) service failed to start")
        print("   2. Apache installation failed during deployment")
        print("   3. Configuration error preventing Apache startup")
        print("   4. Port 80 blocked by firewall")
        print("   5. User/permission issues")
        
        print("\n💡 RECOMMENDED FIXES:")
        print("   1. SSH to instance and check Apache status:")
        print("      ssh -i your-key.pem ec2-user@54.175.20.108")
        print("      sudo systemctl status httpd")
        print("      sudo journalctl -u httpd --no-pager -n 20")
        
        print("\n   2. Try to start Apache manually:")
        print("      sudo systemctl start httpd")
        print("      sudo systemctl enable httpd")
        
        print("\n   3. Check Apache configuration:")
        print("      sudo httpd -t")
        
        print("\n   4. Check firewall:")
        print("      sudo firewall-cmd --list-all")
        print("      sudo firewall-cmd --permanent --add-service=http")
        print("      sudo firewall-cmd --reload")
        
        print("\n   5. Use automated fix script:")
        print("      # Copy fix-lamp-amazon-linux.py to the instance")
        print("      # Run it on the instance to auto-fix common issues")
        
        print("\n   6. Use troubleshooting tools (requires AWS credentials):")
        print("      source .aws-creds.sh")
        print("      python3 troubleshooting-tools/lamp/debug-lamp.py")
        print("      python3 troubleshooting-tools/lamp/fix-lamp.py")
        
    else:
        print("✅ HTTP (port 80) is open - web server is running")
        if success:
            print("✅ Application is responding correctly")
        else:
            print("⚠️  Web server running but application may have issues")
    
    # Check other deployments for comparison
    print("\n🔄 COMPARISON WITH OTHER DEPLOYMENTS:")
    print("=" * 40)
    
    other_deployments = [
        ("React Dashboard v7", "http://52.91.12.91/"),
        ("Python Flask API v7", "http://13.217.21.30/"),
        ("Node.js Application v7", "http://100.31.53.93:3000/"),
        ("Docker LAMP Demo v7", "http://100.31.250.251/"),
    ]
    
    working_count = 0
    for name, url in other_deployments:
        success, status, _ = test_endpoint(url, timeout=5)
        if success:
            print(f"✅ {name}: Working")
            working_count += 1
        else:
            print(f"❌ {name}: Failed ({status})")
    
    print(f"\n📈 Other deployments: {working_count}/{len(other_deployments)} working")
    
    if working_count == len(other_deployments):
        print("✅ All other deployments are working - LAMP issue is isolated")
        print("💡 This confirms the issue is specific to the LAMP stack deployment")
    elif working_count > 0:
        print("⚠️  Most other deployments working - likely LAMP-specific issue")
    else:
        print("❌ Multiple deployments failing - may be broader infrastructure issue")
    
    # Final recommendation
    print("\n🎯 FINAL RECOMMENDATION:")
    print("=" * 25)
    
    if 80 not in open_ports:
        print("🔧 IMMEDIATE ACTION NEEDED:")
        print("   The Apache (httpd) service is not running on the LAMP instance.")
        print("   This is preventing the web application from being accessible.")
        print("")
        print("🚀 QUICKEST FIX:")
        print("   1. Refresh AWS credentials: source .aws-creds.sh")
        print("   2. Run: python3 troubleshooting-tools/lamp/fix-lamp.py")
        print("   3. When prompted, enter: amazon-linux-test-v7-20241220")
        print("   4. Choose to reboot if Apache won't start")
        print("")
        print("📋 ALTERNATIVE (Manual SSH):")
        print("   1. SSH: ssh -i your-key.pem ec2-user@54.175.20.108")
        print("   2. Copy and run fix-lamp-amazon-linux.py on the instance")
        print("")
        print("🔍 ROOT CAUSE ANALYSIS:")
        print("   The deployment succeeded in creating the instance and installing")
        print("   packages, but Apache failed to start properly. This is common")
        print("   on Amazon Linux when there are configuration conflicts or")
        print("   permission issues during the initial setup.")
        
        return 1
    else:
        print("✅ LAMP stack appears to be working correctly!")
        return 0

if __name__ == '__main__':
    sys.exit(main())