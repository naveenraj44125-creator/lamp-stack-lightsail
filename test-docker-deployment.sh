#!/bin/bash
# Test script to diagnose Docker deployment issues

set -e

echo "🔍 Testing Docker Deployment Configuration"
echo "=========================================="

# Check if AWS credentials are configured
echo ""
echo "1. Checking AWS credentials..."
if aws sts get-caller-identity > /dev/null 2>&1; then
    echo "✅ AWS credentials are configured"
    aws sts get-caller-identity
else
    echo "❌ AWS credentials not configured"
    echo "Run: source .aws-creds.sh"
    exit 1
fi

# Check instance status
echo ""
echo "2. Checking Lightsail instance status..."
INSTANCE_NAME="docker-lamp-demo-v1"
REGION="us-east-1"

if aws lightsail get-instance --instance-name "$INSTANCE_NAME" --region "$REGION" > /dev/null 2>&1; then
    echo "✅ Instance $INSTANCE_NAME exists"
    
    # Get instance IP
    INSTANCE_IP=$(aws lightsail get-instance --instance-name "$INSTANCE_NAME" --region "$REGION" --query 'instance.publicIpAddress' --output text)
    echo "   IP Address: $INSTANCE_IP"
    
    # Get instance state
    INSTANCE_STATE=$(aws lightsail get-instance --instance-name "$INSTANCE_NAME" --region "$REGION" --query 'instance.state.name' --output text)
    echo "   State: $INSTANCE_STATE"
    
    # Test SSH connectivity
    echo ""
    echo "3. Testing SSH connectivity..."
    if timeout 10 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 ubuntu@$INSTANCE_IP "echo 'SSH connection successful'" 2>/dev/null; then
        echo "✅ SSH connection successful"
    else
        echo "❌ Cannot connect via SSH"
        echo "   This might be a firewall or key issue"
    fi
    
    # Test HTTP connectivity
    echo ""
    echo "4. Testing HTTP connectivity..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://$INSTANCE_IP/ || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ HTTP connection successful (200)"
    elif [ "$HTTP_CODE" = "000" ]; then
        echo "❌ Cannot connect to HTTP (timeout or connection refused)"
    else
        echo "⚠️  HTTP returned code: $HTTP_CODE"
    fi
    
else
    echo "❌ Instance $INSTANCE_NAME not found"
    exit 1
fi

echo ""
echo "=========================================="
echo "Diagnosis complete!"
