#!/bin/bash

echo "🚀 V5 Deployment Monitor - Live Status"
echo "======================================"
echo ""

# Function to get colored status
get_status_icon() {
    local status="$1"
    local conclusion="$2"
    
    case "$status" in
        "completed")
            case "$conclusion" in
                "success") echo "✅" ;;
                "failure") echo "❌" ;;
                "cancelled") echo "🚫" ;;
                *) echo "❓" ;;
            esac
            ;;
        "in_progress") echo "🔄" ;;
        "queued") echo "⏸️ " ;;
        *) echo "❓" ;;
    esac
}

# Monitor function
monitor_v5_deployments() {
    local iteration=1
    
    while true; do
        clear
        echo "🚀 V5 Deployment Monitor - Live Status (Iteration $iteration)"
        echo "============================================================"
        echo "$(date)"
        echo ""
        
        # Get workflow runs and display status
        gh run list --limit 20 --json status,name,conclusion,workflowName,databaseId,createdAt 2>/dev/null | jq -r '
            .[] | 
            select(.workflowName | test("Deploy|Test|LAMP|Node|Python|React|Nginx|MCP|Recipe")) |
            select(.name | test("🔄 Update all")) |
            "\(.status)|\(.conclusion)|\(.name)|\(.workflowName)|\(.databaseId)"
        ' | head -12 | while IFS='|' read -r status conclusion name workflow id; do
            
            local icon=$(get_status_icon "$status" "$conclusion")
            local workflow_short=$(echo "$workflow" | cut -c1-30)
            
            printf "%-3s %-32s %s\n" "$icon" "$workflow_short" "$status"
        done
        
        echo ""
        echo "📊 SUMMARY"
        echo "----------"
        
        # Count statuses
        local data=$(gh run list --limit 20 --json status,name,conclusion,workflowName 2>/dev/null | jq -r '
            .[] | 
            select(.workflowName | test("Deploy|Test|LAMP|Node|Python|React|Nginx|MCP|Recipe")) |
            select(.name | test("🔄 Update all")) |
            "\(.status)|\(.conclusion)"
        ')
        
        local total=$(echo "$data" | wc -l | tr -d ' ')
        local running=$(echo "$data" | grep -c "in_progress" || echo "0")
        local queued=$(echo "$data" | grep -c "queued" || echo "0")
        local success=$(echo "$data" | grep -c "completed|success" || echo "0")
        local failed=$(echo "$data" | grep -c "completed|failure" || echo "0")
        
        echo "Total: $total | Running: $running | Queued: $queued | Success: $success | Failed: $failed"
        echo ""
        echo "🔄 Refreshing in 15 seconds... (Press Ctrl+C to stop)"
        
        sleep 15
        iteration=$((iteration + 1))
    done
}

# Check dependencies
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "❌ jq not found"
    exit 1
fi

# Start monitoring
monitor_v5_deployments