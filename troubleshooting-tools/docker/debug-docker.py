#!/usr/bin/env python3
"""
Comprehensive Docker deployment debug script
Checks SSH connectivity, Docker status, containers, and application health
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [docker-lamp-demo]: ").strip() or 'docker-lamp-demo'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print("\n🔍 Debugging Docker Deployment")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    debug_script = '''
echo "📋 1. Checking SSH key permissions:"
ls -la ~/.ssh/
echo ""
cat ~/.ssh/authorized_keys | head -5

echo ""
echo "📋 2. Checking Docker service status:"
sudo systemctl status docker --no-pager

echo ""
echo "📋 3. Checking Docker version:"
docker --version
docker-compose --version 2>/dev/null || docker compose version

echo ""
echo "📋 4. Listing all Docker containers:"
docker ps -a

echo ""
echo "📋 5. Checking Docker container logs (last 50 lines):"
docker-compose -f /opt/docker-app/*/docker-compose.yml logs --tail=50 2>/dev/null || echo "No docker-compose found"

echo ""
echo "📋 6. Checking Docker images:"
docker images

echo ""
echo "📋 7. Checking Docker networks:"
docker network ls

echo ""
echo "📋 8. Checking disk space:"
df -h

echo ""
echo "📋 9. Checking Docker system info:"
docker system df

echo ""
echo "📋 10. Testing container connectivity:"
for container in $(docker ps -q); do
    echo "Container: $(docker inspect --format='{{.Name}}' $container)"
    docker exec $container curl -I http://localhost 2>&1 | head -5 || echo "Cannot connect to container"
    echo ""
done

echo ""
echo "📋 11. Checking application directory:"
ls -la /opt/docker-app/

echo ""
echo "📋 12. Testing external connectivity:"
curl -I http://localhost/ 2>&1 | head -10
'''
    
    success, output = client.run_command(debug_script, timeout=180)
    print(output)
    
    if not success:
        print("\n❌ Debug script failed")
        return 1
    
    print("\n✅ Debug complete")
    return 0

if __name__ == '__main__':
    sys.exit(main())
