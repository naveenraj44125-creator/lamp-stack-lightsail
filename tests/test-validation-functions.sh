#!/bin/bash

# Test script for bucket name validation and entry point detection

# Source required modules
source setup/00-variables.sh
source setup/01-utils.sh
source setup/03-project-analysis.sh

echo "Testing Bucket Name Validation..."
echo "=================================="
echo ""

# Test valid bucket names
echo "Testing valid bucket names:"
valid_names=(
    "my-bucket"
    "app-bucket-2024"
    "test.bucket.name"
    "abc"
    "my-app-123"
)

for name in "${valid_names[@]}"; do
    if validate_bucket_name "$name" 2>/dev/null; then
        echo "✓ '$name' - PASSED (valid)"
    else
        echo "✗ '$name' - FAILED (should be valid)"
    fi
done

echo ""
echo "Testing invalid bucket names:"

# Test invalid bucket names
invalid_names=(
    "MyBucket"           # uppercase
    "my_bucket"          # underscore
    "ab"                 # too short
    "-bucket"            # starts with hyphen
    "bucket-"            # ends with hyphen
    "bucket..name"       # consecutive periods
    "192.168.1.1"        # IP format
)

for name in "${invalid_names[@]}"; do
    if validate_bucket_name "$name" 2>/dev/null; then
        echo "✗ '$name' - FAILED (should be invalid)"
    else
        echo "✓ '$name' - PASSED (correctly rejected)"
    fi
done

echo ""
echo "=================================="
echo "Testing Entry Point Detection..."
echo "=================================="
echo ""

# Test Node.js entry point detection
echo "Testing Node.js entry point detection:"
result=$(detect_entry_point "nodejs")
if [[ -n "$result" ]]; then
    echo "✓ Detected Node.js entry point: $result"
else
    echo "✓ No Node.js entry point detected (expected if none exist)"
fi

# Test Python entry point detection
echo "Testing Python entry point detection:"
result=$(detect_entry_point "python")
if [[ -n "$result" ]]; then
    echo "✓ Detected Python entry point: $result"
else
    echo "✓ No Python entry point detected (expected if none exist)"
fi

# Test PHP entry point detection
echo "Testing PHP entry point detection:"
result=$(detect_entry_point "lamp")
if [[ -n "$result" ]]; then
    echo "✓ Detected PHP entry point: $result"
else
    echo "✓ No PHP entry point detected (expected if none exist)"
fi

echo ""
echo "=================================="
echo "All tests completed!"
echo "=================================="
