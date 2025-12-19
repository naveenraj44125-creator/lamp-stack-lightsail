#!/bin/bash

# Monitor MCP Server Deployment
# Usage: ./monitor-mcp-deployment.sh [run-id]

RUN_ID=${1:-20159736970}
WORKFLOW_NAME="Deploy MCP Server to Lightsail"

echo "🚀 Monitoring MCP Server Deployment"
echo "Run ID: $RUN_ID"
echo "Workflow: $WORKFLOW_NAME"
echo "GitHub URL: https://github.com/naveenraj44125-creator/lamp-stack-lightsail/actions/runs/$RUN_ID"
echo "=" * 80

# Function to get run status
get_run_status() {
    gh run view $RUN_ID --json status,conclusion,jobs | jq -r '.status'
}

# Function to display job status
display_jobs() {
    echo "📊 Job Status:"
    gh run view $RUN_ID --json jobs | jq -r '.jobs[] | "  \(.name): \(.status) \(if .conclusion then "(\(.conclusion))" else "" end)"'
    echo ""
}

# Function to get the currently running job
get_current_job() {
    gh run view $RUN_ID --json jobs | jq -r '.jobs[] | select(.status == "in_progress") | .id' | head -1
}

# Monitor loop
while true; do
    STATUS=$(get_run_status)
    
    echo "🔄 Overall Status: $STATUS"
    display_jobs
    
    if [[ "$STATUS" == "completed" ]]; then
        CONCLUSION=$(gh run view $RUN_ID --json conclusion | jq -r '.conclusion')
        if [[ "$CONCLUSION" == "success" ]]; then
            echo "🎉 Deployment completed successfully!"
            
            # Check if MCP server is accessible
            echo "🔍 Checking MCP server accessibility..."
            if curl -s http://18.215.231.164:3000/health > /dev/null; then
                echo "✅ MCP server is accessible at http://18.215.231.164:3000"
                echo "🌐 Web interface: http://18.215.231.164:3000/"
                echo "🔗 SSE endpoint: http://18.215.231.164:3000/sse"
            else
                echo "⚠️  MCP server not yet accessible, may still be starting up"
            fi
        else
            echo "❌ Deployment failed with conclusion: $CONCLUSION"
        fi
        break
    elif [[ "$STATUS" == "failure" ]] || [[ "$STATUS" == "cancelled" ]]; then
        echo "❌ Deployment $STATUS"
        break
    else
        # Show details of currently running job
        CURRENT_JOB=$(get_current_job)
        if [[ -n "$CURRENT_JOB" ]]; then
            echo "🔄 Currently running job details:"
            gh run view --job=$CURRENT_JOB | tail -10
            echo ""
        fi
        
        echo "⏳ Waiting 30 seconds before next check..."
        sleep 30
        echo ""
    fi
done

echo "📋 Final Summary:"
gh run view $RUN_ID