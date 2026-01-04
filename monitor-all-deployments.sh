#!/bin/bash

echo "📊 Monitoring All GitHub Actions Deployments"
echo "============================================"
echo ""

# Source AWS credentials if available
if [ -f ".aws-creds.sh" ]; then
    source .aws-creds.sh
fi

# Function to check deployment status
check_deployments() {
    echo "🔍 Checking deployment status..."
    echo ""
    
    # Get recent workflow runs
    gh run list --limit 20 --json status,name,conclusion,createdAt,url | \
    jq -r '.[] | "\(.status) | \(.name) | \(.conclusion // "running") | \(.createdAt) | \(.url)"' | \
    while IFS='|' read -r status name conclusion created_at url; do
        # Clean up the fields
        status=$(echo "$status" | xargs)
        name=$(echo "$name" | xargs)
        conclusion=$(echo "$conclusion" | xargs)
        created_at=$(echo "$created_at" | xargs)
        url=$(echo "$url" | xargs)
        
        # Format the output with status icons
        case "$conclusion" in
            "success")
                icon="✅"
                ;;
            "failure")
                icon="❌"
                ;;
            "cancelled")
                icon="🚫"
                ;;
            "running"|"in_progress")
                icon="🔄"
                ;;
            *)
                icon="⏳"
                ;;
        esac
        
        printf "%-6s %-50s %-12s\n" "$icon" "$name" "$conclusion"
    done
    
    echo ""
}

# Function to show summary
show_summary() {
    echo "📈 Deployment Summary:"
    echo "====================="
    
    local total=$(gh run list --limit 20 --json status | jq '. | length')
    local success=$(gh run list --limit 20 --json conclusion | jq '[.[] | select(.conclusion == "success")] | length')
    local failed=$(gh run list --limit 20 --json conclusion | jq '[.[] | select(.conclusion == "failure")] | length')
    local running=$(gh run list --limit 20 --json status | jq '[.[] | select(.status == "in_progress")] | length')
    
    echo "Total runs: $total"
    echo "✅ Success: $success"
    echo "❌ Failed: $failed"
    echo "🔄 Running: $running"
    echo ""
}

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "❌ jq is not installed"
    exit 1
fi

# Main monitoring loop
echo "Press Ctrl+C to stop monitoring"
echo ""

while true; do
    clear
    echo "📊 GitHub Actions Deployment Monitor"
    echo "===================================="
    echo "Last updated: $(date)"
    echo ""
    
    check_deployments
    show_summary
    
    echo "Refreshing in 30 seconds... (Ctrl+C to quit)"
    sleep 30
done
