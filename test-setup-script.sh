#!/bin/bash

# Test script for setup-complete-deployment.sh
# This script tests the configuration generation without actually deploying

set -e

echo "🧪 Testing setup-complete-deployment.sh configuration generation..."

# Create a temporary directory for testing
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# Initialize a git repository
git init
git config user.email "test@example.com"
git config user.name "Test User"

# Add a fake remote
git remote add origin https://github.com/test/test-repo.git

# Copy the setup script
cp "$OLDPWD/setup-complete-deployment.sh" .
chmod +x setup-complete-deployment.sh

# Test help functionality
echo "Testing help functionality..."
./setup-complete-deployment.sh --help > /dev/null

# Test configuration generation for each app type
APP_TYPES=("lamp" "nodejs" "python" "react" "docker" "nginx")

for app_type in "${APP_TYPES[@]}"; do
    echo "Testing $app_type configuration generation..."
    
    # Create a minimal test by sourcing the script and calling specific functions
    source ./setup-complete-deployment.sh
    
    # Test create_deployment_config function
    create_deployment_config "$app_type" "Test App" "test-instance" "us-east-1" \
        "ubuntu_22_04" "small_3_0" "mysql" "false" "" "app_db" \
        "test-bucket" "read_write" "small_1_0" "true"
    
    # Check if config file was created
    if [[ -f "deployment-${app_type}.config.yml" ]]; then
        echo "✅ deployment-${app_type}.config.yml created"
        
        # Validate YAML syntax if python is available
        if command -v python3 &> /dev/null; then
            python3 -c "import yaml; yaml.safe_load(open('deployment-${app_type}.config.yml'))" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "✅ deployment-${app_type}.config.yml is valid YAML"
            else
                echo "❌ deployment-${app_type}.config.yml is invalid YAML"
                exit 1
            fi
        fi
    else
        echo "❌ deployment-${app_type}.config.yml not created"
        exit 1
    fi
    
    # Test create_github_workflow function
    mkdir -p .github/workflows
    create_github_workflow "$app_type" "Test App" "us-east-1"
    
    # Check if workflow file was created
    if [[ -f ".github/workflows/deploy-${app_type}.yml" ]]; then
        echo "✅ .github/workflows/deploy-${app_type}.yml created"
        
        # Validate YAML syntax if python is available
        if command -v python3 &> /dev/null; then
            python3 -c "import yaml; yaml.safe_load(open('.github/workflows/deploy-${app_type}.yml'))" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "✅ .github/workflows/deploy-${app_type}.yml is valid YAML"
            else
                echo "❌ .github/workflows/deploy-${app_type}.yml is invalid YAML"
                exit 1
            fi
        fi
    else
        echo "❌ .github/workflows/deploy-${app_type}.yml not created"
        exit 1
    fi
    
    # Test create_example_app function
    create_example_app "$app_type" "Test App"
    
    # Check if example app was created
    if [[ -d "example-${app_type}-app" ]]; then
        echo "✅ example-${app_type}-app directory created"
        
        # Check for main files based on app type
        case $app_type in
            "lamp")
                [[ -f "example-${app_type}-app/index.php" ]] && echo "✅ index.php created" || { echo "❌ index.php missing"; exit 1; }
                ;;
            "nodejs")
                [[ -f "example-${app_type}-app/package.json" ]] && echo "✅ package.json created" || { echo "❌ package.json missing"; exit 1; }
                [[ -f "example-${app_type}-app/app.js" ]] && echo "✅ app.js created" || { echo "❌ app.js missing"; exit 1; }
                ;;
            "python")
                [[ -f "example-${app_type}-app/app.py" ]] && echo "✅ app.py created" || { echo "❌ app.py missing"; exit 1; }
                [[ -f "example-${app_type}-app/requirements.txt" ]] && echo "✅ requirements.txt created" || { echo "❌ requirements.txt missing"; exit 1; }
                ;;
            "react")
                [[ -f "example-${app_type}-app/package.json" ]] && echo "✅ package.json created" || { echo "❌ package.json missing"; exit 1; }
                [[ -f "example-${app_type}-app/src/App.js" ]] && echo "✅ App.js created" || { echo "❌ App.js missing"; exit 1; }
                ;;
            "docker")
                [[ -f "example-${app_type}-app/docker-compose.yml" ]] && echo "✅ docker-compose.yml created" || { echo "❌ docker-compose.yml missing"; exit 1; }
                [[ -f "example-${app_type}-app/Dockerfile" ]] && echo "✅ Dockerfile created" || { echo "❌ Dockerfile missing"; exit 1; }
                ;;
            "nginx")
                [[ -f "example-${app_type}-app/index.html" ]] && echo "✅ index.html created" || { echo "❌ index.html missing"; exit 1; }
                ;;
        esac
    else
        echo "❌ example-${app_type}-app directory not created"
        exit 1
    fi
    
    echo "✅ $app_type configuration test passed"
    echo ""
    
    # Clean up for next test
    rm -f "deployment-${app_type}.config.yml"
    rm -f ".github/workflows/deploy-${app_type}.yml"
    rm -rf "example-${app_type}-app"
done

# Clean up
cd "$OLDPWD"
rm -rf "$TEST_DIR"

echo "🎉 All tests passed! The setup script can generate valid configurations for all application types."