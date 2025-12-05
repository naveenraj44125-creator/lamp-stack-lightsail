#!/bin/bash

# Track all deployment workflows
echo "📊 DEPLOYMENT TRACKER"
echo "===================="
echo ""
echo "Monitoring all example application deployments..."
echo ""

# Function to get status emoji
get_status_emoji() {
    case $1 in
        "completed")
            case $2 in
                "success") echo "✅" ;;
                "failure") echo "❌" ;;
                "cancelled") echo "⚠️" ;;
                "startup_failure") echo "🚫" ;;
                *) echo "❓" ;;
            esac
            ;;
        "in_progress") echo "🔄" ;;
        "queued") echo "⏳" ;;
        "waiting") echo "⏸️" ;;
        *) echo "❓" ;;
    esac
}

# Get latest runs for each workflow
workflows=(
    "deploy-lamp.yml"
    "deploy-nginx.yml"
    "deploy-nodejs.yml"
    "deploy-python.yml"
    "deploy-react.yml"
    "deploy-docker-basic.yml"
    "deploy-recipe-docker.yml"
)

echo "Latest Deployment Status:"
echo "------------------------"

for workflow in "${workflows[@]}"; do
    # Get the latest run for this workflow
    run_data=$(gh run list --workflow="$workflow" --limit 1 --json status,conclusion,name,url,createdAt 2>/dev/null)
    
    if [ -n "$run_data" ] && [ "$run_data" != "[]" ]; then
        status=$(echo "$run_data" | jq -r '.[0].status')
        conclusion=$(echo "$run_data" | jq -r '.[0].conclusion')
        name=$(echo "$run_data" | jq -r '.[0].name')
        url=$(echo "$run_data" | jq -r '.[0].url')
        created=$(echo "$run_data" | jq -r '.[0].createdAt')
        
        emoji=$(get_status_emoji "$status" "$conclusion")
        
        echo "$emoji $name"
        echo "   Status: $status"
        if [ "$status" = "completed" ]; then
            echo "   Result: $conclusion"
        fi
        echo "   URL: $url"
        echo ""
    fi
done

echo ""
echo "Summary:"
echo "--------"

# Count statuses
total=0
success=0
failed=0
in_progress=0
queued=0

for workflow in "${workflows[@]}"; do
    run_data=$(gh run list --workflow="$workflow" --limit 1 --json status,conclusion 2>/dev/null)
    
    if [ -n "$run_data" ] && [ "$run_data" != "[]" ]; then
        total=$((total + 1))
        status=$(echo "$run_data" | jq -r '.[0].status')
        conclusion=$(echo "$run_data" | jq -r '.[0].conclusion')
        
        if [ "$status" = "completed" ]; then
            if [ "$conclusion" = "success" ]; then
                success=$((success + 1))
            else
                failed=$((failed + 1))
            fi
        elif [ "$status" = "in_progress" ]; then
            in_progress=$((in_progress + 1))
        elif [ "$status" = "queued" ] || [ "$status" = "waiting" ]; then
            queued=$((queued + 1))
        fi
    fi
done

echo "Total Workflows: $total"
echo "✅ Successful: $success"
echo "❌ Failed: $failed"
echo "🔄 In Progress: $in_progress"
echo "⏳ Queued: $queued"

echo ""
echo "Run 'gh run list --limit 20' to see all recent runs"
echo "Run './track-deployments.sh' again to refresh status"
