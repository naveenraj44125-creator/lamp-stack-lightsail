#!/bin/bash

echo "🚀 Enhanced Deployment Monitor"
echo "============================="
echo ""

# Function to get colored status
get_colored_status() {
    local status="$1"
    local conclusion="$2"
    
    case "$status" in
        "completed")
            case "$conclusion" in
                "success") echo "✅ SUCCESS" ;;
                "failure") echo "❌ FAILED" ;;
                "cancelled") echo "🚫 CANCELLED" ;;
                *) echo "❓ COMPLETED ($conclusion)" ;;
            esac
            ;;
        "in_progress") echo "🔄 RUNNING" ;;
        "queued") echo "⏸️  QUEUED" ;;
        "requested") echo "📋 REQUESTED" ;;
        *) echo "❓ $status" ;;
    esac
}

# Function to format duration
format_duration() {
    local created="$1"
    local now=$(date -u +%s)
    local created_ts=$(date -d "$created" +%s 2>/dev/null || echo "$now")
    local duration=$((now - created_ts))
    
    if [ $duration -lt 60 ]; then
        echo "${duration}s"
    elif [ $duration -lt 3600 ]; then
        echo "$((duration / 60))m $((duration % 60))s"
    else
        echo "$((duration / 3600))h $((duration % 3600 / 60))m"
    fi
}

# Function to get deployment type from workflow name
get_deployment_type() {
    local name="$1"
    echo "$name" | sed -E 's/.*Deploy ([^-]*).*/\1/' | tr '[:upper:]' '[:lower:]'
}

# Monitor function
monitor_deployments() {
    while true; do
        clear
        echo "🚀 Live Deployment Monitor - $(date)"
        echo "============================================"
        echo ""
        
        # Get recent workflow runs
        local runs=$(gh run list --limit 20 --json status,name,conclusion,createdAt,id,workflowName,updatedAt 2>/dev/null)
        
        if [ $? -ne 0 ]; then
            echo "❌ Failed to fetch workflow runs. Check GitHub CLI authentication."
            echo ""
            echo "Run: gh auth login"
            sleep 10
            continue
        fi
        
        # Filter and display deployment workflows
        echo "$runs" | jq -r '
            .[] | 
            select(.workflowName | test("Deploy|Test")) |
            "\(.status)|\(.conclusion)|\(.name)|\(.workflowName)|\(.createdAt)|\(.id)|\(.updatedAt)"
        ' | head -15 | while IFS='|' read -r status conclusion name workflow created id updated; do
            
            local status_display=$(get_colored_status "$status" "$conclusion")
            local duration=$(format_duration "$created")
            local deployment_type=$(get_deployment_type "$name")
            
            printf "%-15s %s (%s)\n" "$deployment_type" "$status_display" "$duration"
            printf "   📝 %s\n" "$name"
            printf "   🆔 Run ID: %s\n" "$id"
            echo ""
        done
        
        # Summary statistics
        echo "📊 SUMMARY"
        echo "----------"
        local total=$(echo "$runs" | jq '[.[] | select(.workflowName | test("Deploy|Test"))] | length')
        local running=$(echo "$runs" | jq '[.[] | select(.workflowName | test("Deploy|Test")) | select(.status == "in_progress")] | length')
        local success=$(echo "$runs" | jq '[.[] | select(.workflowName | test("Deploy|Test")) | select(.conclusion == "success")] | length')
        local failed=$(echo "$runs" | jq '[.[] | select(.workflowName | test("Deploy|Test")) | select(.conclusion == "failure")] | length')
        
        echo "Total Workflows: $total | Running: $running | Success: $success | Failed: $failed"
        echo ""
        echo "🔄 Auto-refreshing every 30 seconds... (Press Ctrl+C to stop)"
        
        sleep 30
    done
}

# Check dependencies
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "❌ jq is not installed"
    echo "Install: brew install jq (macOS) or apt install jq (Ubuntu)"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# Start monitoring
monitor_deployments