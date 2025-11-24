#!/bin/bash

# Check Lightsail instance connectivity
# Usage: ./check-instance-connectivity.sh <instance-name>

set -e

INSTANCE_NAME=${1:-"python-flask-api"}
REGION="us-east-1"

echo "🔍 Checking connectivity for: $INSTANCE_NAME"
echo ""

# Get instance details
echo "📋 Instance Details:"
aws lightsail get-instance \
    --instance-name "$INSTANCE_NAME" \
    --region "$REGION" \
    --query 'instance.[name,state.name,publicIpAddress,blueprintName]' \
    --output table

# Get IP
IP=$(aws lightsail get-instance \
    --instance-name "$INSTANCE_NAME" \
    --region "$REGION" \
    --query 'instance.publicIpAddress' \
    --output text)

echo ""
echo "🌐 Public IP: $IP"
echo ""

# Check port 22
echo "🔌 Checking Port 22 (SSH):"
timeout 5 nc -zv "$IP" 22 2>&1 || echo "❌ Cannot connect to port 22"
echo ""

# Check port 80
echo "🔌 Checking Port 80 (HTTP):"
timeout 5 nc -zv "$IP" 80 2>&1 || echo "❌ Cannot connect to port 80"
echo ""

# Check firewall rules
echo "🔥 Firewall Rules:"
aws lightsail get-instance-port-states \
    --instance-name "$INSTANCE_NAME" \
    --region "$REGION" \
    --query 'portStates[?state==`open`].[fromPort,protocol,state]' \
    --output table

echo ""
echo "💡 Recommendations:"
echo "1. If SSH (port 22) is not accessible:"
echo "   - Check if instance is fully booted"
echo "   - Verify SSH service is running"
echo "   - Check UFW firewall rules on instance"
echo ""
echo "2. To fix UFW blocking SSH:"
echo "   - Use Lightsail browser-based SSH"
echo "   - Run: sudo ufw allow 22"
echo "   - Run: sudo ufw reload"
echo ""
echo "3. To reset UFW completely:"
echo "   - Run: sudo ufw disable"
echo "   - Run: sudo ufw --force reset"
echo "   - Run: sudo ufw allow 22"
echo "   - Run: sudo ufw allow 80"
echo "   - Run: sudo ufw allow 443"
echo "   - Run: sudo ufw enable"
