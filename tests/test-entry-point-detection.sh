#!/bin/bash

# Test script for entry point detection with actual files

# Source required modules
source setup/00-variables.sh
source setup/01-utils.sh
source setup/03-project-analysis.sh

echo "Testing Entry Point Detection with Files..."
echo "============================================"
echo ""

# Create temporary test directory
TEST_DIR=$(mktemp -d)
echo "Created test directory: $TEST_DIR"
echo ""

# Test 1: Node.js with server.js in root
echo "Test 1: Node.js with server.js in root"
mkdir -p "$TEST_DIR/test1"
touch "$TEST_DIR/test1/server.js"
pushd "$TEST_DIR/test1" > /dev/null
result=$(detect_entry_point "nodejs")
if [[ "$result" == "server.js" ]]; then
    echo "✓ PASSED - Detected: $result"
else
    echo "✗ FAILED - Expected 'server.js', got: '$result'"
fi
popd > /dev/null
echo ""

# Test 2: Node.js with index.js in root (should prefer server.js if both exist)
echo "Test 2: Node.js with both server.js and index.js (priority test)"
mkdir -p "$TEST_DIR/test2"
touch "$TEST_DIR/test2/server.js"
touch "$TEST_DIR/test2/index.js"
pushd "$TEST_DIR/test2" > /dev/null
result=$(detect_entry_point "nodejs")
if [[ "$result" == "server.js" ]]; then
    echo "✓ PASSED - Correctly prioritized: $result"
else
    echo "✗ FAILED - Expected 'server.js', got: '$result'"
fi
popd > /dev/null
echo ""

# Test 3: Node.js with server/server.js
echo "Test 3: Node.js with server/server.js"
mkdir -p "$TEST_DIR/test3/server"
touch "$TEST_DIR/test3/server/server.js"
pushd "$TEST_DIR/test3" > /dev/null
result=$(detect_entry_point "nodejs")
if [[ "$result" == "server/server.js" ]]; then
    echo "✓ PASSED - Detected: $result"
else
    echo "✗ FAILED - Expected 'server/server.js', got: '$result'"
fi
popd > /dev/null
echo ""

# Test 4: Python with app.py
echo "Test 4: Python with app.py"
mkdir -p "$TEST_DIR/test4"
touch "$TEST_DIR/test4/app.py"
pushd "$TEST_DIR/test4" > /dev/null
result=$(detect_entry_point "python")
if [[ "$result" == "app.py" ]]; then
    echo "✓ PASSED - Detected: $result"
else
    echo "✗ FAILED - Expected 'app.py', got: '$result'"
fi
popd > /dev/null
echo ""

# Test 5: Python with src/main.py
echo "Test 5: Python with src/main.py"
mkdir -p "$TEST_DIR/test5/src"
touch "$TEST_DIR/test5/src/main.py"
pushd "$TEST_DIR/test5" > /dev/null
result=$(detect_entry_point "python")
if [[ "$result" == "src/main.py" ]]; then
    echo "✓ PASSED - Detected: $result"
else
    echo "✗ FAILED - Expected 'src/main.py', got: '$result'"
fi
popd > /dev/null
echo ""

# Test 6: PHP with index.php
echo "Test 6: PHP with index.php"
mkdir -p "$TEST_DIR/test6"
touch "$TEST_DIR/test6/index.php"
pushd "$TEST_DIR/test6" > /dev/null
result=$(detect_entry_point "lamp")
if [[ "$result" == "index.php" ]]; then
    echo "✓ PASSED - Detected: $result"
else
    echo "✗ FAILED - Expected 'index.php', got: '$result'"
fi
popd > /dev/null
echo ""

# Test 7: PHP with public/index.php
echo "Test 7: PHP with public/index.php"
mkdir -p "$TEST_DIR/test7/public"
touch "$TEST_DIR/test7/public/index.php"
pushd "$TEST_DIR/test7" > /dev/null
result=$(detect_entry_point "lamp")
if [[ "$result" == "public/index.php" ]]; then
    echo "✓ PASSED - Detected: $result"
else
    echo "✗ FAILED - Expected 'public/index.php', got: '$result'"
fi
popd > /dev/null
echo ""

# Test 8: No entry point
echo "Test 8: No entry point (empty directory)"
mkdir -p "$TEST_DIR/test8"
pushd "$TEST_DIR/test8" > /dev/null
result=$(detect_entry_point "nodejs")
if [[ -z "$result" ]]; then
    echo "✓ PASSED - Correctly returned empty string"
else
    echo "✗ FAILED - Expected empty string, got: '$result'"
fi
popd > /dev/null
echo ""

# Cleanup
rm -rf "$TEST_DIR"
echo "Cleaned up test directory"
echo ""
echo "============================================"
echo "All entry point detection tests completed!"
echo "============================================"
