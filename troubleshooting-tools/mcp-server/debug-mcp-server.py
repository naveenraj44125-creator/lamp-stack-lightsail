#!/usr/bin/env python3
"""
Comprehensive MCP Server deployment debug script
Checks Node.js, systemd service, application files, and connectivity
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [mcp-server-demo]: ").strip() or 'mcp-server-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print("\n🔍 Debugging MCP Server Deployment")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    debug_script = '''
echo "📋 1. Checking Node.js version:"
node --version

echo ""
echo "📋 2. Checking npm version:"
npm --version

echo ""
echo "📋 3. Checking application directory:"
ls -la /opt/nodejs-app/

echo ""
echo "📋 4. Checking package.json:"
cat /opt/nodejs-app/package.json 2>/dev/null || echo "package.json not found"

echo ""
echo "📋 5. Checking installed npm packages:"
cd /opt/nodejs-app && npm list --depth=0 2>&1 | head -30

echo ""
echo "📋 6. Checking systemd service status:"
sudo systemctl status nodejs-app.service --no-pager -l

echo ""
echo "📋 7. Checking systemd service file:"
cat /etc/systemd/system/nodejs-app.service

echo ""
echo "📋 8. Checking service logs (last 50 lines):"
sudo journalctl -u nodejs-app.service -n 50 --no-pager

echo ""
echo "📋 9. Checking application logs:"
echo "=== Output log ==="
sudo tail -30 /var/log/nodejs-app/output.log 2>/dev/null || echo "No output log"
echo ""
echo "=== Error log ==="
sudo tail -30 /var/log/nodejs-app/error.log 2>/dev/null || echo "No error log"

echo ""
echo "📋 10. Checking Node.js process:"
ps aux | grep node | grep -v grep

echo ""
echo "📋 11. Checking port 3000 listener:"
sudo netstat -tlnp | grep :3000 || sudo ss -tlnp | grep :3000 || echo "No process listening on port 3000"

echo ""
echo "📋 12. Testing local connectivity:"
curl -v http://localhost:3000/ 2>&1 | head -20

echo ""
echo "📋 13. Checking firewall rules:"
sudo iptables -L -n | grep 3000 || echo "No iptables rules for port 3000"

echo ""
echo "📋 14. Checking file permissions:"
ls -la /opt/nodejs-app/ | head -20

echo ""
echo "📋 15. Checking environment variables in service:"
sudo systemctl show nodejs-app.service --property=Environment

echo ""
echo "📋 16. Attempting manual start (if service is not running):"
if ! systemctl is-active --quiet nodejs-app.service; then
    echo "Service is not running, attempting manual start..."
    cd /opt/nodejs-app && sudo -u ubuntu node server.js &
    sleep 3
    curl -I http://localhost:3000/ 2>&1 | head -10
    sudo pkill -f "node server.js"
else
    echo "Service is already running"
fi
'''
    
    success, output = client.run_command(debug_script, timeout=120)
    print(output)
    
    if not success:
        print("\n❌ Debug script failed")
        return 1
    
    print("\n✅ Debug complete")
    return 0

if __name__ == '__main__':
    sys.exit(main())
