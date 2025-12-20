#!/bin/bash

echo "🚀 Spinning Up All Example Deployments"
echo "======================================"
echo ""

# Array of all deployment configurations
DEPLOYMENTS=(
    "deployment-lamp-stack.config.yml"
    "deployment-nodejs.config.yml" 
    "deployment-python.config.yml"
    "deployment-react.config.yml"
    "deployment-nginx.config.yml"
    "deployment-docker.config.yml"
    "deployment-recipe-docker.config.yml"
    "deployment-social-media-app.config.yml"
)

# Function to trigger deployment
trigger_deployment() {
    local config_file="$1"
    local app_name=$(echo "$config_file" | sed 's/deployment-//g' | sed 's/.config.yml//g')
    
    echo "🔄 Triggering deployment: $app_name"
    echo "   Config: $config_file"
    
    # Map config files to their specific workflow names
    local workflow_name=""
    case "$app_name" in
        "lamp-stack")
            workflow_name="Deploy LAMP Stack Example"
            ;;
        "nodejs")
            workflow_name="Node.js Application Deployment"
            ;;
        "python")
            workflow_name="Python Flask API Deployment"
            ;;
        "react")
            workflow_name="React Dashboard Deployment"
            ;;
        "nginx")
            workflow_name="Nginx Static Site Deployment"
            ;;
        "docker")
            workflow_name="Deploy Basic Docker LAMP"
            ;;
        "recipe-docker")
            workflow_name="Deploy Recipe Manager Docker App"
            ;;
        "social-media-app")
            workflow_name="Deploy Social Media App"
            ;;
        *)
            echo "   ⚠️  Unknown deployment type: $app_name"
            return 1
            ;;
    esac
    
    # Trigger GitHub Actions workflow
    gh workflow run "$workflow_name"
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Successfully triggered $app_name deployment"
    else
        echo "   ❌ Failed to trigger $app_name deployment"
    fi
    echo ""
    
    # Wait a bit between deployments to avoid overwhelming
    sleep 5
}

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed or not in PATH"
    echo "Please install it: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Please run: gh auth login"
    exit 1
fi

echo "📋 Found ${#DEPLOYMENTS[@]} deployment configurations:"
for config in "${DEPLOYMENTS[@]}"; do
    echo "   - $config"
done
echo ""

read -p "🤔 Do you want to trigger all deployments? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting deployment sequence..."
    echo ""
    
    # Trigger all deployments
    for config in "${DEPLOYMENTS[@]}"; do
        if [ -f "$config" ]; then
            trigger_deployment "$config"
        else
            echo "⚠️  Config file not found: $config"
        fi
    done
    
    echo "🎉 All deployments triggered!"
    echo ""
    echo "📊 Starting monitoring..."
    echo "Use Ctrl+C to stop monitoring"
    echo ""
    
    # Start monitoring
    ./monitor-all-deployments.sh
else
    echo "❌ Deployment cancelled by user"
    exit 0
fi