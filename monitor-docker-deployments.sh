#!/bin/bash
# Monitor Docker deployment workflows

echo "🔍 Monitoring Docker Deployments"
echo "=================================="
echo ""

BASIC_RUN_ID=19937830981
RECIPE_RUN_ID=19937833638

check_status() {
    local run_id=$1
    local name=$2
    
    status=$(gh run view $run_id --json status,conclusion --jq '.status')
    conclusion=$(gh run view $run_id --json status,conclusion --jq '.conclusion')
    
    if [ "$status" = "completed" ]; then
        if [ "$conclusion" = "success" ]; then
            echo "✅ $name: SUCCESS"
            return 0
        else
            echo "❌ $name: FAILED ($conclusion)"
            return 1
        fi
    else
        echo "⏳ $name: In Progress..."
        return 2
    fi
}

while true; do
    clear
    echo "🔍 Docker Deployment Status"
    echo "=================================="
    echo "Time: $(date '+%H:%M:%S')"
    echo ""
    
    check_status $BASIC_RUN_ID "Basic Docker LAMP"
    basic_result=$?
    
    check_status $RECIPE_RUN_ID "Recipe Manager Docker"
    recipe_result=$?
    
    echo ""
    echo "=================================="
    
    # Check if both are complete
    if [ $basic_result -ne 2 ] && [ $recipe_result -ne 2 ]; then
        echo ""
        echo "🎉 Both deployments completed!"
        
        if [ $basic_result -eq 0 ] && [ $recipe_result -eq 0 ]; then
            echo "✅ All deployments successful!"
            
            # Get instance IPs
            echo ""
            echo "📍 Instance Information:"
            source .aws-creds.sh 2>/dev/null
            aws lightsail get-instances --region us-east-1 --query 'instances[?contains(name, `docker`)].{Name:name, IP:publicIpAddress, State:state.name}' --output table 2>/dev/null || echo "Could not fetch instance info"
        else
            echo "⚠️  Some deployments failed. Check logs for details."
        fi
        break
    fi
    
    echo "Refreshing in 30 seconds... (Ctrl+C to stop)"
    sleep 30
done
