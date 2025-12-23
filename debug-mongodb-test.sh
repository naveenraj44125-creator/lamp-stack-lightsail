#!/bin/bash
# Debug script to test MongoDB config generation

source ./setup-complete-deployment.sh 2>/dev/null

echo "Testing create_deployment_config with mongodb..."
create_deployment_config "nodejs" "Test App" "test-instance" "us-east-1" "ubuntu_22_04" "small_3_0" "mongodb" "false" "" "testdb" "" "" "" "false"

echo ""
echo "=== Checking for MONGODB_URI ==="
if grep -q "MONGODB_URI" deployment-nodejs.config.yml; then
    echo "✓ MONGODB_URI found!"
    grep "MONGODB" deployment-nodejs.config.yml
else
    echo "✗ MONGODB_URI NOT found"
    echo ""
    echo "=== Environment variables section ==="
    grep -A15 "environment_variables" deployment-nodejs.config.yml
fi

# Cleanup
rm -f deployment-nodejs.config.yml
