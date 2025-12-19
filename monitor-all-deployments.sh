#!/bin/bash

echo "📊 Monitoring All Deployment Workflows"
echo "====================================="
echo ""

# Array of workflow files to monitor
WORKFLOWS=(
    "deploy-lamp.yml"
    "deploy-nodejs.yml" 
    "deploy-python.yml"
    "deploy-react.yml"
    "deploy-nginx.yml"
    "deploy-docker-basic.yml"
    "deploy-recipe-docker.yml"
    "deploy-mcp-server.yml"
    "test-amazon-linux.yml"
)

# Function to check workflow status
check_workflow_status() {
    local workflow="$1"
    echo "🔍 Checking $workflow..."
    
    # Get the latest run for this workflow
    gh run list --workflow="$workflow" --limit=1 --json status,conclusion,createdAt,url 2>/dev/null | \
    jq -r '.[] | "   Status: \(.status) | Conclusion: \(.conclusion // "N/A") | Created: \(.createdAt) | URL: \(.url)"' 2>/dev/null || \
    echo "   ⚠️  Could not fetch status for $workflow"
    
    echo ""
}

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed or not in PATH"
    exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "⚠️  jq is not installed - output will be less formatted"
    echo "Install jq for better output: brew install jq (macOS) or apt install jq (Ubuntu)"
    echo ""
fi

echo "🚀 Monitoring deployment workflows..."
echo "Press Ctrl+C to stop monitoring"
echo ""

# Monitor loop
while true; do
    echo "📊 Workflow Status Check - $(date)"
    echo "================================"
    
    for workflow in "${WORKFLOWS[@]}"; do
        check_workflow_status "$workflow"
    done
    
    echo "⏳ Waiting 30 seconds before next check..."
    echo ""
    sleep 30
done