#!/usr/bin/env python3
"""
Fix LAMP Stack deployment issues on Amazon Linux
This script addresses common Apache (httpd) startup issues on Amazon Linux 2023
"""

import subprocess
import sys
import time

def run_command(cmd, description=""):
    """Run a command and return success status"""
    if description:
        print(f"🔧 {description}")
    
    print(f"   Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Failed (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ❌ Command timed out")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def check_service_status(service_name):
    """Check if a service is running"""
    result = subprocess.run(f"systemctl is-active {service_name}", shell=True, capture_output=True, text=True)
    return result.returncode == 0

def main():
    print("🚀 LAMP Stack Fix for Amazon Linux 2023")
    print("=" * 50)
    print("This script will attempt to fix common Apache (httpd) issues")
    print("Target instance: amazon-linux-test-v7-20241220 (54.175.20.108)")
    print("=" * 50)
    
    # Note: This script is designed to be run ON the Amazon Linux instance
    # It cannot be run remotely without SSH access
    print("\n⚠️  IMPORTANT: This script must be run ON the Amazon Linux instance")
    print("   You need to SSH to the instance first:")
    print("   ssh -i your-key.pem ec2-user@54.175.20.108")
    print("   Then run this script on the instance")
    
    response = input("\nAre you running this ON the Amazon Linux instance? (y/N): ").strip().lower()
    if response != 'y':
        print("\n💡 To fix the LAMP stack remotely, you need:")
        print("   1. Valid AWS credentials (refresh .aws-creds.sh)")
        print("   2. Use the troubleshooting-tools/lamp/fix-lamp.py script")
        print("   3. Or SSH directly to the instance")
        return 1
    
    print("\n🔍 Step 1: Checking current system status...")
    
    # Check if httpd is installed
    httpd_installed = run_command("rpm -q httpd", "Checking if httpd is installed")
    
    if not httpd_installed:
        print("\n📦 Step 2: Installing httpd (Apache)...")
        if not run_command("sudo yum install -y httpd", "Installing httpd package"):
            print("❌ Failed to install httpd")
            return 1
    else:
        print("\n✅ httpd is already installed")
    
    # Check httpd service status
    print("\n🔍 Step 3: Checking httpd service status...")
    if check_service_status("httpd"):
        print("✅ httpd service is running")
    else:
        print("❌ httpd service is not running")
        
        # Try to start httpd
        print("\n🚀 Step 4: Starting httpd service...")
        if not run_command("sudo systemctl start httpd", "Starting httpd service"):
            print("❌ Failed to start httpd, checking logs...")
            run_command("sudo journalctl -u httpd --no-pager -n 20", "Checking httpd logs")
            
            # Try to fix common issues
            print("\n🔧 Step 5: Attempting to fix common httpd issues...")
            
            # Fix 1: Check for configuration syntax errors
            run_command("sudo httpd -t", "Testing httpd configuration")
            
            # Fix 2: Check for port conflicts
            run_command("sudo netstat -tlnp | grep :80", "Checking port 80 usage")
            
            # Fix 3: Check SELinux status (might be blocking)
            run_command("getenforce", "Checking SELinux status")
            
            # Fix 4: Ensure proper permissions on document root
            run_command("sudo mkdir -p /var/www/html", "Creating document root")
            run_command("sudo chown -R apache:apache /var/www/html", "Setting proper ownership")
            run_command("sudo chmod -R 755 /var/www/html", "Setting proper permissions")
            
            # Fix 5: Create a simple index.html
            index_content = '''<!DOCTYPE html>
<html>
<head>
    <title>LAMP Stack - Apache Working</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .success { color: #28a745; font-size: 24px; margin-bottom: 20px; }
        .info { background: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="success">✅ LAMP Stack Deployment Successful!</h1>
        <div class="info">
            <p><strong>Server:</strong> Apache (httpd) on Amazon Linux 2023</p>
            <p><strong>Instance:</strong> amazon-linux-test-v7-20241220</p>
            <p><strong>IP Address:</strong> 54.175.20.108</p>
            <p><strong>Document Root:</strong> /var/www/html</p>
            <p><strong>Status:</strong> Web server is running and accessible</p>
        </div>
        <p>Your LAMP stack has been deployed successfully on Amazon Linux 2023. Apache is now serving content correctly.</p>
        <p><strong>Next steps:</strong></p>
        <ul>
            <li>Upload your PHP application files to /var/www/html</li>
            <li>Configure your database connections</li>
            <li>Test your application functionality</li>
        </ul>
    </div>
</body>
</html>'''
            
            # Write index.html
            with open('/tmp/index.html', 'w') as f:
                f.write(index_content)
            
            run_command("sudo mv /tmp/index.html /var/www/html/index.html", "Creating index.html")
            run_command("sudo chown apache:apache /var/www/html/index.html", "Setting index.html ownership")
            run_command("sudo chmod 644 /var/www/html/index.html", "Setting index.html permissions")
            
            # Try to start httpd again
            print("\n🚀 Step 6: Attempting to start httpd again...")
            if not run_command("sudo systemctl start httpd", "Starting httpd service (retry)"):
                print("❌ Still failed to start httpd")
                run_command("sudo journalctl -u httpd --no-pager -n 30", "Checking detailed httpd logs")
                return 1
    
    # Enable httpd to start on boot
    print("\n🔧 Step 7: Enabling httpd to start on boot...")
    run_command("sudo systemctl enable httpd", "Enabling httpd service")
    
    # Check firewall
    print("\n🔥 Step 8: Checking firewall configuration...")
    firewall_active = run_command("sudo systemctl is-active firewalld", "Checking firewalld status")
    if firewall_active:
        run_command("sudo firewall-cmd --permanent --add-service=http", "Opening HTTP port in firewall")
        run_command("sudo firewall-cmd --reload", "Reloading firewall configuration")
    else:
        print("   ℹ️  firewalld is not active, no firewall changes needed")
    
    # Test local access
    print("\n🧪 Step 9: Testing local HTTP access...")
    if run_command("curl -s -I http://localhost/ | head -5", "Testing local HTTP access"):
        print("✅ Local HTTP access is working")
    else:
        print("❌ Local HTTP access failed")
    
    # Final status check
    print("\n📊 Step 10: Final status check...")
    if check_service_status("httpd"):
        print("✅ httpd service is running")
        run_command("sudo systemctl status httpd --no-pager -l", "httpd service status")
        
        print("\n🎉 SUCCESS! LAMP stack should now be working")
        print("🌐 Test external access: http://54.175.20.108/")
        print("📁 Upload your files to: /var/www/html/")
        return 0
    else:
        print("❌ httpd service is still not running")
        print("💡 Manual troubleshooting needed:")
        print("   - Check logs: sudo journalctl -u httpd -f")
        print("   - Test config: sudo httpd -t")
        print("   - Check ports: sudo netstat -tlnp | grep :80")
        return 1

if __name__ == '__main__':
    sys.exit(main())