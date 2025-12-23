#!/usr/bin/env python3
"""
Debug script for Instagram Clone deployment
Checks Node.js, PM2, environment variables, and application status
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [instagram-clone]: ").strip() or 'instagram-clone'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print(f"\n🔍 Debugging Instagram Clone Deployment on {instance_name}")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    debug_script = '''
echo "========================================"
echo "📋 1. SYSTEM INFO"
echo "========================================"
echo "Hostname: $(hostname)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Uptime: $(uptime)"

echo ""
echo "========================================"
echo "📋 2. NODE.JS & NPM VERSIONS"
echo "========================================"
node --version 2>&1 || echo "Node.js not found"
npm --version 2>&1 || echo "npm not found"

echo ""
echo "========================================"
echo "📋 3. PM2 STATUS"
echo "========================================"
pm2 status 2>&1 || echo "PM2 not installed or not running"

echo ""
echo "========================================"
echo "📋 4. APPLICATION DIRECTORY CONTENTS"
echo "========================================"
echo "--- /opt/nodejs-app/ ---"
ls -la /opt/nodejs-app/ 2>/dev/null || echo "Directory not found"

echo ""
echo "--- /var/www/html/ ---"
ls -la /var/www/html/ 2>/dev/null || echo "Directory not found"

echo ""
echo "========================================"
echo "📋 5. ENVIRONMENT FILES"
echo "========================================"
echo "--- /opt/nodejs-app/.env ---"
cat /opt/nodejs-app/.env 2>/dev/null || echo "File not found"

echo ""
echo "--- /var/www/html/.env ---"
cat /var/www/html/.env 2>/dev/null || echo "File not found"

echo ""
echo "--- /etc/environment.d/app.conf ---"
cat /etc/environment.d/app.conf 2>/dev/null || echo "File not found"

echo ""
echo "========================================"
echo "📋 6. PM2 ECOSYSTEM CONFIG"
echo "========================================"
cat /opt/nodejs-app/ecosystem.config.cjs 2>/dev/null || cat /opt/nodejs-app/ecosystem.config.js 2>/dev/null || echo "ecosystem.config.cjs not found"

echo ""
echo "========================================"
echo "📋 7. PM2 LOGS (last 50 lines)"
echo "========================================"
pm2 logs --lines 50 --nostream 2>&1 || echo "No PM2 logs available"

echo ""
echo "========================================"
echo "📋 8. APPLICATION ERROR LOG"
echo "========================================"
cat /var/log/nodejs-app/error.log 2>/dev/null | tail -50 || echo "No error log found"

echo ""
echo "========================================"
echo "📋 9. APPLICATION OUTPUT LOG"
echo "========================================"
cat /var/log/nodejs-app/output.log 2>/dev/null | tail -30 || echo "No output log found"

echo ""
echo "========================================"
echo "📋 10. PACKAGE.JSON"
echo "========================================"
cat /opt/nodejs-app/package.json 2>/dev/null || echo "package.json not found"

echo ""
echo "========================================"
echo "📋 11. SERVER.JS (first 50 lines)"
echo "========================================"
head -50 /opt/nodejs-app/server.js 2>/dev/null || echo "server.js not found"

echo ""
echo "========================================"
echo "📋 12. LISTENING PORTS"
echo "========================================"
sudo ss -tlnp 2>/dev/null || sudo netstat -tlnp 2>/dev/null || echo "Cannot check ports"

echo ""
echo "========================================"
echo "📋 13. NODE PROCESSES"
echo "========================================"
ps aux | grep -E "node|pm2" | grep -v grep || echo "No node processes found"

echo ""
echo "========================================"
echo "📋 14. NGINX STATUS"
echo "========================================"
sudo systemctl status nginx --no-pager 2>&1 || echo "Nginx not installed"

echo ""
echo "========================================"
echo "📋 15. NGINX CONFIG"
echo "========================================"
cat /etc/nginx/sites-enabled/nodejs-app 2>/dev/null || cat /etc/nginx/sites-enabled/default 2>/dev/null || echo "No nginx config found"

echo ""
echo "========================================"
echo "📋 16. LOCAL CONNECTIVITY TEST"
echo "========================================"
echo "Testing localhost:3000..."
curl -v http://localhost:3000/ 2>&1 | head -30

echo ""
echo "Testing localhost:80..."
curl -v http://localhost:80/ 2>&1 | head -30

echo ""
echo "========================================"
echo "📋 17. SYSTEMD SERVICE (if exists)"
echo "========================================"
sudo systemctl status nodejs-app.service --no-pager 2>&1 || echo "No systemd service"

echo ""
echo "========================================"
echo "📋 18. DISK SPACE"
echo "========================================"
df -h

echo ""
echo "========================================"
echo "📋 19. MEMORY USAGE"
echo "========================================"
free -h

echo ""
echo "========================================"
echo "📋 DEBUG COMPLETE"
echo "========================================"
'''
    
    success, output = client.run_command(debug_script, timeout=180)
    print(output)
    
    if not success:
        print("\n❌ Debug script failed to execute")
        return 1
    
    print("\n✅ Debug complete")
    return 0

if __name__ == '__main__':
    sys.exit(main())
