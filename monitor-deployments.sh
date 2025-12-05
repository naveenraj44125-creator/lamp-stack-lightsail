#!/bin/bash

echo "🔍 Starting continuous deployment monitoring..."
echo "Press Ctrl+C to stop"
echo ""

while true; do
    clear
    ./track-deployments.sh
    echo ""
    echo "⏰ Last updated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "🔄 Refreshing in 30 seconds..."
    sleep 30
done
