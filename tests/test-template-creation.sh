#!/bin/bash

# Test script to verify template creation is skipped when entry points exist

# Source required modules
source setup/00-variables.sh
source setup/01-utils.sh
source setup/02-ui.sh
source setup/03-project-analysis.sh
source setup/06-config-generation.sh

echo "Testing Template Creation Logic..."
echo "==================================="
echo ""

# Create temporary test directory
TEST_DIR=$(mktemp -d)
echo "Created test directory: $TEST_DIR"
echo ""

# Test 1: Node.js project with existing server.js - should skip template creation
echo "Test 1: Node.js with existing server.js"
mkdir -p "$TEST_DIR/test1"
pushd "$TEST_DIR/test1" > /dev/null
echo "console.log('existing server');" > server.js
echo "Running create_example_app..."
create_example_app "nodejs" "TestApp" 2>&1 | grep -q "Detected existing entry point"
if [[ $? -eq 0 ]]; then
    echo "✓ PASSED - Correctly detected existing entry point"
    if [[ ! -f "app.js" ]]; then
        echo "✓ PASSED - app.js was NOT created (correct behavior)"
    else
        echo "✗ FAILED - app.js was created (should have been skipped)"
    fi
else
    echo "✗ FAILED - Did not detect existing entry point"
fi
popd > /dev/null
echo ""

# Test 2: Node.js project with no entry points - should create templates
echo "Test 2: Node.js with no entry points"
mkdir -p "$TEST_DIR/test2"
pushd "$TEST_DIR/test2" > /dev/null
echo "Running create_example_app..."
create_example_app "nodejs" "TestApp" > /dev/null 2>&1
if [[ -f "app.js" ]]; then
    echo "✓ PASSED - app.js was created (correct behavior)"
else
    echo "✗ FAILED - app.js was NOT created (should have been created)"
fi
if [[ -f "package.json" ]]; then
    echo "✓ PASSED - package.json was created"
else
    echo "✗ FAILED - package.json was NOT created"
fi
popd > /dev/null
echo ""

# Test 3: Python project with existing app.py - should skip template creation
echo "Test 3: Python with existing app.py"
mkdir -p "$TEST_DIR/test3"
pushd "$TEST_DIR/test3" > /dev/null
echo "print('existing app')" > app.py
echo "Running create_example_app..."
create_example_app "python" "TestApp" 2>&1 | grep -q "Detected existing entry point"
if [[ $? -eq 0 ]]; then
    echo "✓ PASSED - Correctly detected existing entry point"
    # Count app.py files (should only be the one we created)
    app_count=$(ls -1 app.py 2>/dev/null | wc -l)
    if [[ $app_count -eq 1 ]]; then
        echo "✓ PASSED - No duplicate app.py created"
    else
        echo "✗ FAILED - Duplicate files may have been created"
    fi
else
    echo "✗ FAILED - Did not detect existing entry point"
fi
popd > /dev/null
echo ""

# Test 4: PHP project with existing index.php - should skip template creation
echo "Test 4: PHP with existing index.php"
mkdir -p "$TEST_DIR/test4"
pushd "$TEST_DIR/test4" > /dev/null
echo "<?php echo 'existing'; ?>" > index.php
echo "Running create_example_app..."
create_example_app "lamp" "TestApp" 2>&1 | grep -q "Detected existing entry point"
if [[ $? -eq 0 ]]; then
    echo "✓ PASSED - Correctly detected existing entry point"
    # Count index.php files (should only be the one we created)
    php_count=$(ls -1 index.php 2>/dev/null | wc -l)
    if [[ $php_count -eq 1 ]]; then
        echo "✓ PASSED - No duplicate index.php created"
    else
        echo "✗ FAILED - Duplicate files may have been created"
    fi
else
    echo "✗ FAILED - Did not detect existing entry point"
fi
popd > /dev/null
echo ""

# Cleanup
rm -rf "$TEST_DIR"
echo "Cleaned up test directory"
echo ""
echo "==================================="
echo "All template creation tests completed!"
echo "==================================="
