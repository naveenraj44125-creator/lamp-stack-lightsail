#!/bin/bash
# Download Lightsail SSH key

REGION="us-east-1"
KEY_FILE="$HOME/.ssh/LightsailDefaultKey-$REGION.pem"

echo "🔑 Downloading Lightsail SSH Key"
echo "=================================="

# Download the key
aws lightsail download-default-key-pair \
  --region "$REGION" \
  --query 'privateKeyBase64' \
  --output text | base64 -d > "$KEY_FILE"

if [ $? -eq 0 ]; then
  # Set correct permissions
  chmod 600 "$KEY_FILE"
  echo "✅ Key downloaded to: $KEY_FILE"
  echo "✅ Permissions set to 600"
  
  # Test the key
  echo ""
  echo "🧪 Testing key..."
  ssh-keygen -l -f "$KEY_FILE"
  
  echo ""
  echo "✅ Key is ready to use!"
else
  echo "❌ Failed to download key"
  exit 1
fi
