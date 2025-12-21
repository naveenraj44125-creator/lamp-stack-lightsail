#!/bin/bash

echo "📊 Monitoring All GitHub Actions Deployments"
echo "============================================"
echo ""

# Source AWS credentials if available
if [ -f ".aws-creds.sh" ]; then
    source .aws-creds.sh
fi

# Function to run endpoint verification
run_endpoint_verification() {
    echo "🔍 Running Endpoint Verification..."
    echo ""
    python3 quick-endpoint-check.py
    echo ""
}

# Function to check deployment status with endpoint verification
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
        
        # Format timestamp
        timestamp=$(date -d "$created_at" "+%H:%M:%S" 2>/dev/null || echo "$created_at")
        
        printf "%-6s %-50s %-12s %s\n" "$icon" "$name" "$conclusion" "$timestamp"
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

# Main monitoring loop
echo "Available commands:"
echo "  - Press 'v' + Enter to run endpoint verification"
echo "  - Press 'f' + Enter to run nginx fix (via troubleshooting tools)"
echo "  - Press 'q' + Enter to quit"
echo "  - Press Ctrl+C to stop monitoring"
echo ""

# Function to handle user input
handle_input() {
    while true; do
        read -t 1 -n 1 input 2>/dev/null
        if [ $? -eq 0 ]; then
            case "$input" in
                'v'|'V')
                    echo ""
                    echo "🔍 Running endpoint verification..."
                    run_endpoint_verification
                    ;;
                'f'|'F')
                    echo ""
                    echo "🔧 Running nginx fixes via troubleshooting tools..."
                    echo "Note: Use the troubleshooting tools in troubleshooting-tools/ directory"
                    echo "      for manual fixes with proper SSH key setup."
                    ;;
                'q'|'Q')
                    echo ""
                    echo "👋 Exiting monitor..."
                    exit 0
                    ;;
            esac
        fi
        sleep 1
    done
}

# Start input handler in background
handle_input &
INPUT_PID=$!

# Cleanup function
cleanup() {
    kill $INPUT_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

while true; do
    clear
    echo "📊 GitHub Actions Deployment Monitor"
    echo "===================================="
    echo "Last updated: $(date)"
    echo ""
    
    check_deployments
    show_summary
    
    echo "Commands: [v]erify endpoints, [f]ix nginx, [q]uit"
    echo "Refreshing in 30 seconds..."
    sleep 30
done

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

# Main monitoring loop
echo "Available commands:"
echo "  - Press 'v' + Enter to run endpoint verification"
echo "  - Press 'f' + Enter to run nginx fix (via troubleshooting tools)"
echo "  - Press 'q' + Enter to quit"
echo "  - Press Ctrl+C to stop monitoring"
echo ""

# Function to handle user input
handle_input() {
    while true; do
        read -t 1 -n 1 input 2>/dev/null
        if [ $? -eq 0 ]; then
            case "$input" in
                'v'|'V')
                    echo ""
                    echo "🔍 Running endpoint verification..."
                    run_endpoint_verification
                    ;;
                'f'|'F')
                    echo ""
                    echo "🔧 Running nginx fixes via troubleshooting tools..."
                    echo "Note: Use the troubleshooting tools in troubleshooting-tools/ directory"
                    echo "      for manual fixes with proper SSH key setup."
                    ;;
                'q'|'Q')
                    echo ""
                    echo "👋 Exiting monitor..."
                    exit 0
                    ;;
            esac
        fi
        sleep 1
    done
}

# Start input handler in background
handle_input &
INPUT_PID=$!

# Cleanup function
cleanup() {
    kill $INPUT_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

while true; do
    clear
    echo "📊 GitHub Actions Deployment Monitor"
    echo "===================================="
    echo "Last updated: $(date)"
    echo ""
    
    check_deployments
    show_summary
    
    echo "Commands: [v]erify endpoints, [f]ix nginx, [q]uit"
    echo "Refreshing in 30 seconds..."
    sleep 30
done

while true; do
    clear
    echo "📊 GitHub Actions Deployment Monitor"
    echo "===================================="
    echo "Last updated: $(date)"
    echo ""
    
    check_deployments
    show_summary
    
    echo "Refreshing in 30 seconds..."
    sleep 30
done