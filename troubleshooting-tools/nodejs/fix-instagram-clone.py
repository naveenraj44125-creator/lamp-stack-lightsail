#!/usr/bin/env python3
"""
Fix script for Instagram Clone deployment
Fixes environment variable name mismatch: BUCKET_NAME vs S3_BUCKET_NAME
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflows.lightsail_common import LightsailBase

def main():
    instance_name = input("Instance name [instagram-clone-app]: ").strip() or 'instagram-clone-app'
    region = input("AWS region [us-east-1]: ").strip() or 'us-east-1'
    
    print(f"\n🔧 Fixing Instagram Clone Deployment on {instance_name}")
    print("=" * 80)
    
    client = LightsailBase(instance_name, region)
    
    fix_script = '''
set -e
echo "🔧 Fixing Instagram Clone environment variables..."

# The issue: server.js uses S3_BUCKET_NAME but .env has BUCKET_NAME
# Fix: Add S3_BUCKET_NAME to .env file

echo ""
echo "📋 Current .env file:"
cat /opt/nodejs-app/.env

echo ""
echo "🔧 Adding S3_BUCKET_NAME to .env..."

# Check if S3_BUCKET_NAME already exists
if grep -q "S3_BUCKET_NAME" /opt/nodejs-app/.env; then
    echo "✅ S3_BUCKET_NAME already exists in .env"
else
    # Get BUCKET_NAME value and add S3_BUCKET_NAME
    BUCKET_VALUE=$(grep "BUCKET_NAME=" /opt/nodejs-app/.env | cut -d'=' -f2 | tr -d '"')
    echo "S3_BUCKET_NAME=\"$BUCKET_VALUE\"" >> /opt/nodejs-app/.env
    echo "✅ Added S3_BUCKET_NAME=$BUCKET_VALUE"
fi

# Also add AWS credentials if missing (needed for S3 access)
if ! grep -q "AWS_ACCESS_KEY_ID" /opt/nodejs-app/.env; then
    echo ""
    echo "⚠️  AWS_ACCESS_KEY_ID not found in .env"
    echo "   The app needs AWS credentials to access S3"
fi

if ! grep -q "AWS_SECRET_ACCESS_KEY" /opt/nodejs-app/.env; then
    echo "⚠️  AWS_SECRET_ACCESS_KEY not found in .env"
    echo "   The app needs AWS credentials to access S3"
fi

echo ""
echo "📋 Updated .env file:"
cat /opt/nodejs-app/.env

echo ""
echo "🔄 Restarting PM2 app..."
pm2 delete all 2>/dev/null || true
pm2 start /opt/nodejs-app/ecosystem.config.js

echo ""
echo "⏳ Waiting for app to start..."
sleep 5

echo ""
echo "📊 PM2 Status:"
pm2 status

echo ""
echo "📋 PM2 Logs (last 20 lines):"
pm2 logs --lines 20 --nostream 2>&1 || true

echo ""
echo "🔍 Checking if app is listening..."
sudo ss -tlnp | grep -E "3000|5000" || echo "App not listening on port 3000 or 5000"

echo ""
echo "🧪 Testing local connection..."
curl -s http://localhost:5000/ 2>&1 | head -10 || echo "Connection to port 5000 failed"
curl -s http://localhost:3000/ 2>&1 | head -10 || echo "Connection to port 3000 failed"

echo ""
echo "✅ Fix script completed"
'''
    
    success, output = client.run_command(fix_script, timeout=120)
    print(output)
    
    if not success:
        print("\n❌ Fix script failed")
        return 1
    
    print("\n✅ Fix complete")
    return 0

if __name__ == '__main__':
    sys.exit(main())
