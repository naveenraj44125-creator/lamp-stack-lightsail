#!/bin/bash

# Demo script to show smart recommendations in action

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Smart Recommendations Demo                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "This demo shows how the setup script analyzes your project"
echo "and provides intelligent recommendations."
echo ""

# Create a sample project
echo "Creating sample Node.js + React project with MySQL..."
mkdir -p demo-project
cd demo-project

cat > package.json << 'EOF'
{
  "name": "my-fullstack-app",
  "dependencies": {
    "react": "^18.2.0",
    "express": "^4.18.2",
    "mysql2": "^3.6.0",
    "multer": "^1.4.5",
    "cors": "^2.8.5"
  },
  "scripts": {
    "start": "node server.js",
    "build": "cd client && npm run build"
  }
}
EOF

cat > server.js << 'EOF'
const express = require('express');
const multer = require('multer');
const mysql = require('mysql2');

const app = express();
const upload = multer({ dest: 'uploads/' });

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: Date.now() });
});

// File upload endpoint
app.post('/api/upload', upload.single('file'), (req, res) => {
  res.json({ success: true, file: req.file });
});

// Database connection
const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
EOF

mkdir -p client
cat > client/package.json << 'EOF'
{
  "name": "client",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
EOF

echo ""
echo "Running project analysis..."
echo ""

# Source modules and run analysis
source ../setup/00-variables.sh
source ../setup/01-utils.sh
source ../setup/03-project-analysis.sh

analyze_project_for_recommendations .

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "What the script detected:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✓ React + Express (fullstack application)"
echo "✓ MySQL database driver (mysql2)"
echo "✓ File upload library (multer)"
echo "✓ Health endpoint at /api/health"
echo "✓ Recommended instance: small_3_0 (due to database + multiple frameworks)"
echo ""
echo "These recommendations will be:"
echo "  • Highlighted with ★ in interactive menus"
echo "  • Pre-selected as defaults"
echo "  • Used to auto-configure deployment settings"
echo ""

# Cleanup
cd ..
rm -rf demo-project

echo "Demo complete!"
