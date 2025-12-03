#!/bin/bash
# Verification script for S3 bucket integration
# Run this on your Lightsail instance after deployment

set -e

BUCKET_NAME="${BUCKET_NAME:-lamp-stack-demo-bucket}"
TEST_FILE="test-$(date +%s).txt"

echo "🔍 Verifying S3 Bucket Integration"
echo "===================================="
echo ""

# Check AWS CLI
echo "1. Checking AWS CLI..."
if ! command -v aws &> /dev/null; then
    echo "   ❌ AWS CLI not found"
    echo "   Install with: sudo apt-get install -y awscli"
    exit 1
fi
echo "   ✅ AWS CLI is installed"
echo ""

# Check AWS credentials
echo "2. Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "   ❌ AWS credentials not configured"
    echo "   Bucket should be attached to instance via Lightsail"
    exit 1
fi
echo "   ✅ AWS credentials are configured"
echo ""

# Check bucket exists
echo "3. Checking bucket exists..."
if ! aws s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
    echo "   ❌ Bucket '$BUCKET_NAME' not found or not accessible"
    exit 1
fi
echo "   ✅ Bucket '$BUCKET_NAME' is accessible"
echo ""

# Test write access
echo "4. Testing write access..."
echo "Test file created at $(date)" > "/tmp/$TEST_FILE"
if aws s3 cp "/tmp/$TEST_FILE" "s3://$BUCKET_NAME/test/$TEST_FILE" &> /dev/null; then
    echo "   ✅ Write access confirmed"
else
    echo "   ❌ Write access failed"
    echo "   Check bucket access level (should be read_write)"
    exit 1
fi
echo ""

# Test read access
echo "5. Testing read access..."
if aws s3 cp "s3://$BUCKET_NAME/test/$TEST_FILE" "/tmp/${TEST_FILE}.download" &> /dev/null; then
    echo "   ✅ Read access confirmed"
else
    echo "   ❌ Read access failed"
    exit 1
fi
echo ""

# Test delete access
echo "6. Testing delete access..."
if aws s3 rm "s3://$BUCKET_NAME/test/$TEST_FILE" &> /dev/null; then
    echo "   ✅ Delete access confirmed"
else
    echo "   ❌ Delete access failed"
    exit 1
fi
echo ""

# List bucket contents
echo "7. Listing bucket contents..."
FILE_COUNT=$(aws s3 ls "s3://$BUCKET_NAME/" --recursive | wc -l)
echo "   📁 Total files in bucket: $FILE_COUNT"
echo ""

# Clean up
rm -f "/tmp/$TEST_FILE" "/tmp/${TEST_FILE}.download"

echo "===================================="
echo "✅ All bucket integration tests passed!"
echo "===================================="
echo ""
echo "Bucket Manager: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/bucket-manager.php"
echo ""
echo "You can now:"
echo "  • Upload files via the web interface"
echo "  • Download files from the bucket"
echo "  • Delete files as needed"
echo "  • Use AWS CLI for advanced operations"
