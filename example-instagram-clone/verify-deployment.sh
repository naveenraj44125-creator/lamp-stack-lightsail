#!/bin/bash

echo "🔍 Instagram Clone Deployment Verification"
echo "=========================================="

# Check current directory
echo "📂 Current directory: $(pwd)"
echo "📁 Directory contents:"
ls -la

# Check if we're in the right location
if [ -f "package.json" ]; then
    echo "✅ Found package.json"
else
    echo "❌ package.json not found"
    echo "🔍 Searching for package.json:"
    find /opt -name "package.json" 2>/dev/null | head -5
fi

# Check Node.js and npm
echo ""
echo "🔧 Environment Check:"
echo "Node.js version: $(node --version 2>/dev/null || echo 'Not found')"
echo "NPM version: $(npm --version 2>/dev/null || echo 'Not found')"

# Check if build directory exists
echo ""
echo "🏗️  Build Status:"
if [ -d "build" ]; then
    echo "✅ Build directory exists"
    echo "📊 Build size: $(du -sh build/)"
    if [ -f "build/index.html" ]; then
        echo "✅ index.html exists"
        echo "📄 First few lines of index.html:"
        head -3 build/index.html
    else
        echo "❌ index.html missing"
    fi
    echo "📁 Build contents:"
    ls -la build/ | head -10
else
    echo "❌ Build directory not found"
    echo "🔍 Searching for build directories:"
    find /opt -name "build" -type d 2>/dev/null | head -5
fi

# Check PM2 status
echo ""
echo "🚀 Process Status:"
if command -v pm2 > /dev/null; then
    echo "PM2 processes:"
    pm2 status
else
    echo "❌ PM2 not found"
fi

# Check if server is running
echo ""
echo "🌐 Server Status:"
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Server responding on port 3000"
    echo "Health check response:"
    curl -s http://localhost:3000/api/health | head -5
else
    echo "❌ Server not responding on port 3000"
fi

# Check nginx status
echo ""
echo "🔧 Nginx Status:"
if systemctl is-active nginx > /dev/null 2>&1; then
    echo "✅ Nginx is running"
else
    echo "❌ Nginx is not running"
fi

echo ""
echo "🔍 Verification complete!"