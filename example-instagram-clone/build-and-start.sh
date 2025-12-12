#!/bin/bash
set -e

echo "🏗️  Starting Instagram Clone build and deployment..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Working directory: $(pwd)"
echo "📂 Directory contents:"
ls -la

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in $(pwd)"
    echo "📁 Available files:"
    ls -la
    exit 1
fi

# Install dependencies (including dev dependencies for build)
echo "📦 Installing dependencies..."
npm ci --production=false

# Verify React Scripts is available
echo "🔍 Checking React Scripts..."
if npm list react-scripts > /dev/null 2>&1; then
    echo "✅ React Scripts found"
else
    echo "❌ React Scripts not found, installing..."
    npm install react-scripts
fi

# Build React app
echo "🔨 Building React application..."
export NODE_ENV=production
export GENERATE_SOURCEMAP=false
export CI=false

npm run build

# Verify build was successful
if [ -d "build" ] && [ -f "build/index.html" ]; then
    echo "✅ React build successful!"
    echo "📊 Build size: $(du -sh build/)"
    echo "📁 Build contents:"
    ls -la build/ | head -10
    echo "📄 Index.html preview:"
    head -5 build/index.html
else
    echo "❌ React build failed - build directory or index.html missing"
    echo "📁 Current directory contents:"
    ls -la
    echo "📁 Looking for build directory:"
    find . -name "build" -type d 2>/dev/null || echo "No build directory found"
    exit 1
fi

# Stop any existing PM2 processes
echo "🛑 Stopping existing processes..."
pm2 delete instagram-clone 2>/dev/null || echo "No existing process to stop"

# Start the server with PM2
echo "🚀 Starting Node.js server..."
pm2 start server.js --name instagram-clone --log-date-format="YYYY-MM-DD HH:mm:ss Z"
pm2 save

echo "✅ Instagram Clone deployment complete!"
echo "🌐 Server should be available at http://localhost:3000"
echo "📊 PM2 status:"
pm2 status

# Test the server is responding
echo "🧪 Testing server response..."
sleep 5
curl -f http://localhost:3000/api/health || echo "⚠️  Health check failed"