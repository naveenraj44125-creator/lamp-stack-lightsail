#!/usr/bin/env python3
"""
Enhanced endpoint verification script with nginx fix capability
"""

import requests
import subprocess
import sys
import time
import json
from typing import Dict, Tuple, Optional

class EndpointVerifier:
    def __init__(self):
        # Deployment endpoint mappings
        self.endpoints = {
            "React Dashboard": {
                "url": "http://35.171.85.222/",
                "expected": "react",
                "instance": "react-dashboard-v6"
            },
            "Python Flask API": {
                "url": "http://18.232.114.213/",
                "expected": "Flask",
                "instance": "python-flask-api-v6"
            },
            "Python Health Endpoint": {
                "url": "http://18.232.114.213/api/health",
                "expected": "healthy",
                "instance": "python-flask-api-v6"
            },
            "Nginx Static Demo": {
                "url": "http://18.215.255.226/",
                "expected": "Welcome to Nginx",
                "instance": "nginx-static-demo-v6"
            },
            "Node.js Application": {
                "url": "http://3.95.21.139:3000/",
                "expected": "Node.js",
                "instance": "simple-blog-1766109629"
            }
        }
        
        # Nginx default page indicators
        self.nginx_default_indicators = [
            "welcome to nginx",
            "nginx.*default",
            "test page for the nginx",
            "nginx http server",
            "default nginx page"
        ]
    
    def test_endpoint(self, name: str, config: Dict) -> Tuple[bool, str, bool]:
        """
        Test an endpoint and return (success, message, is_nginx_default)
        """
        url = config["url"]
        expected = config.get("expected", "")
        
        print(f"\n🧪 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, timeout=15)
            content = response.text.lower()
            
            if response.status_code == 200:
                # Check for nginx default page
                is_nginx_default = any(indicator in content for indicator in self.nginx_default_indicators)
                
                if is_nginx_default:
                    return False, f"⚠️  NGINX DEFAULT PAGE DETECTED - Application not properly configured!", True
                elif expected and expected.lower() in content:
                    return True, f"✅ {name}: HTTP 200 OK - Expected content found", False
                elif not expected:
                    return True, f"✅ {name}: HTTP 200 OK - Response received", False
                else:
                    return False, f"⚠️  {name}: HTTP 200 OK but expected content '{expected}' not found", False
            else:
                return False, f"❌ {name}: HTTP {response.status_code}", False
                
        except requests.exceptions.Timeout:
            return False, f"❌ {name}: Connection timeout", False
        except requests.exceptions.ConnectionError:
            return False, f"❌ {name}: Connection failed", False
        except Exception as e:
            return False, f"❌ {name}: Error - {str(e)}", False
    
    def get_instance_ip(self, instance_name: str) -> Optional[str]:
        """Get the public IP of a Lightsail instance"""
        try:
            cmd = [
                "aws", "lightsail", "get-instance",
                "--instance-name", instance_name,
                "--query", "instance.publicIpAddress",
                "--output", "text"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                ip = result.stdout.strip()
                return ip if ip != "None" else None
            else:
                print(f"❌ Failed to get IP for {instance_name}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout getting IP for {instance_name}")
            return None
        except Exception as e:
            print(f"❌ Error getting IP for {instance_name}: {str(e)}")
            return None
    
    def fix_nginx_configuration(self, instance_name: str) -> bool:
        """Apply nginx fix to remove default server block"""
        print(f"🔧 Applying nginx fix to instance: {instance_name}")
        
        # Get instance IP
        instance_ip = self.get_instance_ip(instance_name)
        if not instance_ip:
            print(f"❌ Could not get IP for instance {instance_name}")
            return False
        
        print(f"📡 Connecting to {instance_ip} to fix nginx configuration...")
        
        # Create nginx fix script
        nginx_fix_script = '''#!/bin/bash
set -e

echo "🔧 Fixing nginx configuration..."

# Backup original nginx.conf if not already backed up
if [ ! -f /etc/nginx/nginx.conf.original ]; then
    sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.original
    echo "✅ Backed up original nginx.conf"
fi

# Completely remove the default server block from nginx.conf
sudo python3 << 'PYTHON_EOF'
import re

# Read the original nginx.conf
with open('/etc/nginx/nginx.conf', 'r') as f:
    content = f.read()

# Find and completely remove the server block within the http context
lines = content.split('\\n')
new_lines = []
in_server_block = False
brace_count = 0

for line in lines:
    stripped = line.strip()
    
    # Check if we're starting a server block
    if 'server' in stripped and '{' in stripped and not in_server_block:
        # This is the start of a server block - skip it entirely
        in_server_block = True
        brace_count = stripped.count('{') - stripped.count('}')
        continue
    
    if in_server_block:
        # Count braces to know when server block ends
        brace_count += line.count('{') - line.count('}')
        
        # If brace count reaches 0, we've closed the server block
        if brace_count <= 0:
            in_server_block = False
        continue
    
    # Keep all other lines
    new_lines.append(line)

# Write the new content without the server block
new_content = '\\n'.join(new_lines)
with open('/etc/nginx/nginx.conf', 'w') as f:
    f.write(new_content)

print("✅ Completely removed default server block from nginx.conf")
PYTHON_EOF

# Remove default files
sudo rm -f /etc/nginx/conf.d/default.conf
sudo rm -f /usr/share/nginx/html/index.html

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

echo "✅ Nginx configuration fixed and restarted"
'''
        
        try:
            # Write fix script to temp file
            with open('/tmp/nginx_fix.sh', 'w') as f:
                f.write(nginx_fix_script)
            
            # Try ubuntu user first, then ec2-user
            users_to_try = ['ubuntu', 'ec2-user']
            
            for user in users_to_try:
                try:
                    # Copy script to instance
                    scp_cmd = [
                        "scp", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=30",
                        "/tmp/nginx_fix.sh", f"{user}@{instance_ip}:/tmp/"
                    ]
                    result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        # Execute script on instance
                        ssh_cmd = [
                            "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=30",
                            f"{user}@{instance_ip}", "chmod +x /tmp/nginx_fix.sh && /tmp/nginx_fix.sh"
                        ]
                        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=120)
                        
                        if result.returncode == 0:
                            print("✅ Nginx fix applied successfully")
                            return True
                        else:
                            print(f"❌ Failed to execute nginx fix: {result.stderr}")
                    else:
                        print(f"❌ Failed to copy script with user {user}: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    print(f"❌ Timeout with user {user}")
                    continue
                except Exception as e:
                    print(f"❌ Error with user {user}: {str(e)}")
                    continue
            
            print("❌ Failed to apply nginx fix with any user")
            return False
            
        except Exception as e:
            print(f"❌ Error applying nginx fix: {str(e)}")
            return False
    
    def run_verification(self, fix_nginx: bool = True) -> bool:
        """Run comprehensive endpoint verification"""
        print("🚀 Running Comprehensive Endpoint Verification")
        print("=" * 50)
        
        results = []
        all_working = True
        
        for name, config in self.endpoints.items():
            success, message, is_nginx_default = self.test_endpoint(name, config)
            print(message)
            
            if not success:
                all_working = False
                
                if is_nginx_default and fix_nginx:
                    instance_name = config.get("instance")
                    if instance_name:
                        print(f"🔧 Nginx default page detected, applying fix...")
                        if self.fix_nginx_configuration(instance_name):
                            print("✅ Fix applied, re-verifying endpoint...")
                            time.sleep(15)  # Wait for nginx to restart
                            
                            success, message, _ = self.test_endpoint(name, config)
                            print(f"Re-verification: {message}")
                            
                            if success:
                                all_working = True  # Fixed successfully
                        else:
                            print("❌ Failed to apply nginx fix")
            
            results.append((name, success))
        
        print("\n" + "=" * 50)
        print("📊 FINAL RESULTS")
        print("=" * 50)
        
        for name, success in results:
            status = "✅ WORKING" if success else "❌ FAILED"
            print(f"{name}: {status}")
        
        print("\n" + "=" * 50)
        if all_working:
            print("🎉 ALL ENDPOINTS ARE FULLY FUNCTIONAL!")
            print("✅ GitHub Actions should now work without issues")
        else:
            print("⚠️  Some endpoints still have issues")
            print("💡 Try running with --fix-nginx to automatically fix nginx issues")
        print("=" * 50)
        
        return all_working

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify deployment endpoints")
    parser.add_argument("--fix-nginx", action="store_true", 
                       help="Automatically fix nginx configuration issues")
    parser.add_argument("--no-fix", action="store_true",
                       help="Skip nginx fixes, just verify endpoints")
    
    args = parser.parse_args()
    
    verifier = EndpointVerifier()
    
    # Source AWS credentials if available
    try:
        subprocess.run(["source", ".aws-creds.sh"], shell=True, check=False)
    except:
        pass
    
    fix_nginx = args.fix_nginx or not args.no_fix
    success = verifier.run_verification(fix_nginx=fix_nginx)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())