#!/bin/bash
# Helper script to copy and run the LAMP fix script on the instance

set -e

echo "🚀 LAMP Stack Fix Helper"
echo "========================"

# Source AWS credentials
source .aws-creds.sh

# Get instance IP
INSTANCE_IP=$(aws lightsail get-instance --instance-name lamp-stack-demo-v2 --region us-east-1 --query 'instance.publicIpAddress' --output text)
echo "Instance IP: $INSTANCE_IP"

# Get SSH key and certificate
echo "Getting SSH key..."
aws lightsail get-instance-access-details --instance-name lamp-stack-demo-v2 --region us-east-1 > /tmp/access.json
cat /tmp/access.json | jq -r '.accessDetails.certKey' > /tmp/lamp-key.pem
cat /tmp/access.json | jq -r '.accessDetails.ipAddress' > /dev/null
chmod 600 /tmp/lamp-key.pem

# Also get the certificate if available
if cat /tmp/access.json | jq -e '.accessDetails.certKey' > /dev/null; then
    cat /tmp/access.json | jq -r '.accessDetails.certKey' > /tmp/lamp-cert.pub
fi

# Copy fix script to instance
echo "Copying fix script to instance..."
scp -i /tmp/lamp-key.pem -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    fix-lamp-deployment.py ubuntu@$INSTANCE_IP:/home/ubuntu/

# Run fix script on instance
echo "Running fix script on instance..."
ssh -i /tmp/lamp-key.pem -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    ubuntu@$INSTANCE_IP "sudo python3 /home/ubuntu/fix-lamp-deployment.py"

# Test connectivity
echo ""
echo "Testing HTTP connectivity..."
sleep 3
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 http://$INSTANCE_IP/ || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Application is responding! HTTP $HTTP_CODE"
    echo "   URL: http://$INSTANCE_IP/"
else
    echo "❌ Application not responding. HTTP $HTTP_CODE"
fi

# Cleanup
rm -f /tmp/lamp-key.pem

echo ""
echo "Done!"
