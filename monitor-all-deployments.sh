#!/bin/bash

echo "🚀 Monitoring All Deployment Workflows"
echo "======================================"
echo ""

# Function to get workflow status with colors
get_status() {
    local status="$1"
    case "$status" in
        "✓") echo "✅ SUCCESS" ;;
        "X") echo "❌ FAILED" ;;
        "*") echo "🔄 RUNNING" ;;
        "-") echo "⏸️  QUEUED" ;;
        *) echo "❓ $status" ;;
    esac
}

# Monitor deployments
while true; do
    clear
    echo "🚀 Deployment Status Monitor - $(date)"
    echo "======================================"
    echo ""
    
    # Get current runs
    gh run list --limit 15 --json status,name,conclusion,createdAt,id,workflowName | jq -r '
        .[] | 
        select(.workflowName | test("Deploy|React|Node|Python|Nginx|MCP|LAMP|Recipe")) |
        "\(.status)\t\(.name)\t\(.workflowName)\t\(.createdAt)\t\(.id)"
    ' | while IFS=$'\t' read -r status name workflow created id; do
        status_display=$(get_status "$status")
        echo "$(echo "$workflow" | cut -c1-20 | printf "%-20s") $status_display"
    done
    
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    echo "Refreshing in 30 seconds..."
    
    sleep 30
done