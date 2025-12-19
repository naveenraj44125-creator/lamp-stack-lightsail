#!/bin/bash

# Monitor the MCP server deployment after syntax fix
RUN_ID="20160802799"
REPO="naveenraj44125-creator/lamp-stack-lightsail"

echo "🔍 Monitoring MCP Server Deployment (Syntax Fix)"
echo "Run ID: $RUN_ID"
echo "Repository: $REPO"
echo "URL: https://github.com/$REPO/actions/runs/$RUN_ID"
echo "=" * 60

# Function to check deployment status
check_status() {
    curl -s "https://api.github.com/repos/$REPO/actions/runs/$RUN_ID" | \
    jq -r '.status, .conclusion, .created_at, .updated_at'
}

# Function to get job status
get_jobs() {
    curl -s "https://api.github.com/repos/$REPO/actions/runs/$RUN_ID/jobs" | \
    jq -r '.jobs[] | "\(.name): \(.status) - \(.conclusion // "running")"'
}

# Monitor until completion
while true; do
    echo "⏰ $(date '+%H:%M:%S') - Checking deployment status..."
    
    STATUS_INFO=$(check_status)
    STATUS=$(echo "$STATUS_INFO" | head -1)
    CONCLUSION=$(echo "$STATUS_INFO" | head -2 | tail -1)
    
    echo "📊 Status: $STATUS"
    if [ "$CONCLUSION" != "null" ]; then
        echo "🎯 Conclusion: $CONCLUSION"
    fi
    
    echo "📋 Jobs:"
    get_jobs | sed 's/^/   /'
    
    if [ "$STATUS" = "completed" ]; then
        echo ""
        if [ "$CONCLUSION" = "success" ]; then
            echo "🎉 Deployment completed successfully!"
            echo "🧪 Running connectivity tests..."
            python3 test-mcp-server-deployment.py
        else
            echo "❌ Deployment failed with conclusion: $CONCLUSION"
            echo "🔗 Check logs: https://github.com/$REPO/actions/runs/$RUN_ID"
        fi
        break
    fi
    
    echo "⏳ Waiting 30 seconds before next check..."
    echo ""
    sleep 30
done