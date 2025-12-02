#!/usr/bin/env python3
"""
Fix LAMP Stack deployment configuration
Run this on the Lightsail instance to fix deployment issues
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print output"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"⚠️  Exit code: {result.returncode}")
    else:
        print("✅ Success")
    
    return result.returncode == 0

def main():
    print("="*60)
    print("🔧 LAMP Stack Deployment Fix Script")
    print("="*60)
    
    # Check if running on the server
    if not os.path.exists('/home/ubuntu'):
        print("\n⚠️  This script should be run on the Lightsail instance")
        print("Copy this script to the server and run it there")
        sys.exit(1)
    
    # 1. Check Apache status
    print("\n📊 Checking Apache status...")
    run_command('sudo systemctl status apache2 --no-pager | head -20', "Apache status")
    
    # 2. Check if application files exist
    print("\n📁 Checking application files...")
    run_command('ls -la /var/www/html/', "Application directory")
    
    # 3. Ensure Apache is installed and running
    run_command('sudo systemctl start apache2', "Starting Apache")
    run_command('sudo systemctl enable apache2', "Enabling Apache on boot")
    
    # 4. Check PHP installation
    print("\n🐘 Checking PHP...")
    run_command('php -v', "PHP version")
    run_command('php -m | grep -E "pdo|pgsql|curl|mbstring"', "PHP extensions")
    
    # 5. Fix permissions
    print("\n🔐 Fixing permissions...")
    run_command('sudo chown -R www-data:www-data /var/www/html', "Setting ownership")
    run_command('sudo chmod -R 755 /var/www/html', "Setting permissions")
    
    # 6. Check firewall
    print("\n🔥 Checking firewall...")
    run_command('sudo ufw status', "Firewall status")
    run_command('sudo ufw allow 80/tcp', "Allowing HTTP")
    
    # 7. Check Apache configuration
    print("\n⚙️  Checking Apache configuration...")
    run_command('apache2ctl -S 2>&1 | head -20', "Apache virtual hosts")
    run_command('sudo apache2ctl configtest', "Apache config test")
    
    # 8. Check Apache error log
    print("\n📋 Checking Apache error log...")
    run_command('sudo tail -30 /var/log/apache2/error.log', "Recent errors")
    
    # 9. Restart Apache
    print("\n🔄 Restarting Apache...")
    run_command('sudo systemctl restart apache2', "Restarting Apache")
    
    # 10. Check if port 80 is listening
    print("\n🔍 Checking port 80...")
    run_command('sudo netstat -tlnp | grep :80', "Port 80 status")
    
    # 11. Test local connectivity
    print("\n🧪 Testing local connectivity...")
    import time
    time.sleep(2)
    
    run_command('curl -v http://localhost/', "Testing HTTP locally")
    
    # 12. Check if index.php exists
    print("\n📄 Checking for index files...")
    run_command('ls -la /var/www/html/index.*', "Index files")
    
    # 13. If no index.php, create a test file
    if not os.path.exists('/var/www/html/index.php'):
        print("\n📝 Creating test index.php...")
        test_php = """<?php
phpinfo();
?>"""
        with open('/tmp/index.php', 'w') as f:
            f.write(test_php)
        run_command('sudo mv /tmp/index.php /var/www/html/index.php', "Creating test PHP file")
        run_command('sudo chown www-data:www-data /var/www/html/index.php', "Setting ownership")
    
    print("\n" + "="*60)
    print("✅ Fix Complete!")
    print("="*60)
    print("\nTest from your local machine:")
    print("  curl http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/")
    print("\nTo view logs:")
    print("  sudo tail -f /var/log/apache2/error.log")
    print("  sudo tail -f /var/log/apache2/access.log")

if __name__ == "__main__":
    main()
