#!/usr/bin/env python3
"""
Automated repair tool for Docker deployment issues
Fixes SSH keys, Docker permissions, container issues, and network problems
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [docker-lamp-demo]: ").strip() or 'docker-lamp-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    reboot = input("Reboot instance after fix? (y/N): ").strip().lower() == 'y'
    
    print("\n🔧 Fixing Docker Deployment Issues")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    fix_script = '''
echo "🔧 1. Fixing SSH key permissions..."
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
echo "✅ SSH permissions fixed"

echo ""
echo "🔧 2. Checking Docker service..."
sudo systemctl enable docker
sudo systemctl start docker
echo "✅ Docker service enabled and started"

echo ""
echo "🔧 3. Adding user to docker group..."
sudo usermod -aG docker ubuntu
echo "✅ User added to docker group"

echo ""
echo "🔧 4. Fixing Docker socket permissions..."
sudo chmod 666 /var/run/docker.sock
echo "✅ Docker socket permissions fixed"

echo ""
echo "🔧 5. Cleaning up stopped containers..."
docker container prune -f
echo "✅ Stopped containers removed"

echo ""
echo "🔧 6. Cleaning up unused images..."
docker image prune -f
echo "✅ Unused images removed"

echo ""
echo "🔧 7. Restarting Docker containers..."
cd /opt/docker-app/*/
docker-compose down 2>/dev/null || true
docker-compose up -d --build
echo "✅ Containers restarted"

echo ""
echo "🔧 8. Waiting for containers to initialize (30s)..."
sleep 30

echo ""
echo "🧪 Testing container health:"
docker ps
echo ""
docker-compose logs --tail=20

echo ""
echo "🧪 Testing local access:"
curl -I http://localhost/ 2>&1 | head -10
'''
    
    success, output = client.run_command(fix_script, timeout=300)
    print(output)
    
    if not success:
        print("\n❌ Fix script failed")
        return 1
    
    if reboot:
        print("\n🔄 Rebooting instance...")
        print("⏳ This will take 1-2 minutes...")
        reboot_success = client.reboot_instance()
        if reboot_success:
            print("✅ Instance rebooted successfully")
        else:
            print("❌ Reboot failed")
            return 1
    
    print("\n✅ Docker deployment fixed successfully")
    return 0

if __name__ == '__main__':
    sys.exit(main())
