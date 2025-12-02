#!/bin/bash

# Setup New GitHub Repository for AWS Lightsail Deployment
# This script creates a new repository with deployment workflows based on selected dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   AWS Lightsail Deployment Repository Setup               ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v gh &> /dev/null; then
    echo -e "${RED}✗ GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi
echo -e "${GREEN}✓ GitHub CLI found${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Git found${NC}"

# Check if logged in to GitHub
if ! gh auth status &> /dev/null; then
    echo -e "${RED}✗ Not logged in to GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi
echo -e "${GREEN}✓ GitHub CLI authenticated${NC}"
echo ""

# Get repository information
echo -e "${BLUE}Repository Information:${NC}"
read -p "Repository name: " REPO_NAME
read -p "Repository description (optional): " REPO_DESC
read -p "Make repository private? (y/N): " PRIVATE_REPO

if [[ "$PRIVATE_REPO" =~ ^[Yy]$ ]]; then
    VISIBILITY="--private"
else
    VISIBILITY="--public"
fi

echo ""
echo -e "${BLUE}Application Configuration:${NC}"
read -p "Application name: " APP_NAME
read -p "Application version (default: 1.0.0): " APP_VERSION
APP_VERSION=${APP_VERSION:-1.0.0}

echo ""
echo -e "${BLUE}AWS Configuration:${NC}"
read -p "AWS Region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}
read -p "Lightsail Instance Name: " INSTANCE_NAME
read -p "AWS IAM Role ARN for GitHub Actions: " AWS_ROLE_ARN

echo ""
echo -e "${BLUE}Select Application Type:${NC}"
echo "1) LAMP Stack (Apache + PHP + MySQL)"
echo "2) Nginx Static Site"
echo "3) Node.js Application (with PM2)"
echo "4) Python/Flask Application (with Gunicorn)"
echo "5) React Application (SPA)"
read -p "Choose application type (1-5): " APP_TYPE_CHOICE

case $APP_TYPE_CHOICE in
    1)
        APP_TYPE="lamp"
        APP_TYPE_NAME="LAMP Stack"
        DEPENDENCIES="apache,php,mysql"
        ;;
    2)
        APP_TYPE="nginx"
        APP_TYPE_NAME="Nginx Static"
        DEPENDENCIES="nginx"
        ;;
    3)
        APP_TYPE="nodejs"
        APP_TYPE_NAME="Node.js"
        DEPENDENCIES="nodejs,pm2"
        ;;
    4)
        APP_TYPE="python"
        APP_TYPE_NAME="Python/Flask"
        DEPENDENCIES="python,nginx"
        ;;
    5)
        APP_TYPE="react"
        APP_TYPE_NAME="React"
        DEPENDENCIES="nodejs,nginx"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}Additional Dependencies:${NC}"
read -p "Enable Git? (Y/n): " ENABLE_GIT
ENABLE_GIT=${ENABLE_GIT:-Y}
if [[ "$ENABLE_GIT" =~ ^[Yy]$ ]]; then
    DEPENDENCIES="$DEPENDENCIES,git"
fi

read -p "Enable Certbot (SSL)? (y/N): " ENABLE_CERTBOT
if [[ "$ENABLE_CERTBOT" =~ ^[Yy]$ ]]; then
    DEPENDENCIES="$DEPENDENCIES,certbot"
fi

echo ""
echo -e "${YELLOW}Summary:${NC}"
echo "Repository: $REPO_NAME"
echo "Application: $APP_NAME ($APP_TYPE_NAME)"
echo "Instance: $INSTANCE_NAME"
echo "Region: $AWS_REGION"
echo "Dependencies: $DEPENDENCIES"
echo ""
read -p "Proceed with setup? (Y/n): " CONFIRM
CONFIRM=${CONFIRM:-Y}

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Setup cancelled"
    exit 0
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo ""
echo -e "${GREEN}Creating repository structure...${NC}"

# Create directory structure
mkdir -p .github/workflows
mkdir -p "example-${APP_TYPE}-app"

# Create deployment config file
cat > "deployment-${APP_TYPE}.config.yml" << EOF
# Deployment Configuration for ${APP_TYPE_NAME} Application
application:
  name: "${APP_NAME}"
  type: "${APP_TYPE}"
  version: "${APP_VERSION}"
  
  # Files to package for deployment
  package_files:
    - "example-${APP_TYPE}-app/**"
  
  # Fallback to packaging all files if specific files not found
  package_fallback: true

aws:
  region: "${AWS_REGION}"

lightsail:
  instance_name: "${INSTANCE_NAME}"
  
  # Instance will be auto-created if it doesn't exist
  auto_create: true
  blueprint_id: "ubuntu_22_04"
  bundle_id: "nano_3_0"  # 512 MB RAM, 1 vCPU, 20 GB SSD

dependencies:
EOF

# Add dependencies based on selection
IFS=',' read -ra DEPS <<< "$DEPENDENCIES"
for dep in "${DEPS[@]}"; do
    dep=$(echo "$dep" | xargs) # trim whitespace
    cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  ${dep}:
    enabled: true
EOF
done

# Add deployment directory
cat >> "deployment-${APP_TYPE}.config.yml" << EOF

deployment:
  target_directory: "/var/www/${APP_TYPE}-app"
  
  # Post-deployment commands (optional)
  post_deploy_commands: []

github_actions:
  jobs:
    test:
      enabled: true
EOF

# Create main workflow file
cat > ".github/workflows/deploy-${APP_TYPE}.yml" << 'WORKFLOW_EOF'
name: APPLICATION_NAME Deployment

on:
  push:
    branches: [ main ]
    paths:
      - 'example-APP_TYPE-app/**'
      - 'deployment-APP_TYPE.config.yml'
      - '.github/workflows/deploy-APP_TYPE.yml'
  workflow_dispatch:

permissions:
  id-token: write   # Required for OIDC authentication
  contents: read    # Required to checkout code

jobs:
  deploy:
    name: Deploy APPLICATION_NAME
    uses: naveenraj44125-creator/lamp-stack-lightsail/.github/workflows/deploy-generic-reusable.yml@main
    with:
      config_file: 'deployment-APP_TYPE.config.yml'
      skip_tests: false
  
  summary:
    name: Deployment Summary
    needs: deploy
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Show Deployment Results
        run: |
          echo "## 🚀 APPLICATION_NAME Deployment" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "- **URL**: ${{ needs.deploy.outputs.deployment_url }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Status**: ${{ needs.deploy.outputs.deployment_status }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          
          if [ "${{ needs.deploy.outputs.deployment_status }}" = "success" ]; then
            echo "✅ Application deployed successfully!" >> $GITHUB_STEP_SUMMARY
          else
            echo "❌ Deployment failed. Check logs above." >> $GITHUB_STEP_SUMMARY
          fi
WORKFLOW_EOF

# Replace placeholders in workflow
sed -i.bak "s/APPLICATION_NAME/${APP_TYPE_NAME}/g" ".github/workflows/deploy-${APP_TYPE}.yml"
sed -i.bak "s/APP_TYPE/${APP_TYPE}/g" ".github/workflows/deploy-${APP_TYPE}.yml"
rm ".github/workflows/deploy-${APP_TYPE}.yml.bak"

# Create example application based on type
case $APP_TYPE in
    lamp)
        cat > "example-lamp-app/index.php" << 'PHP_EOF'
<?php
header('Content-Type: application/json');
echo json_encode([
    'status' => 'success',
    'message' => 'LAMP Stack Application Running',
    'php_version' => phpversion(),
    'timestamp' => date('Y-m-d H:i:s')
]);
?>
PHP_EOF
        ;;
    
    nginx)
        cat > "example-nginx-app/index.html" << 'HTML_EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nginx Static Site</title>
</head>
<body>
    <h1>Welcome to Nginx Static Site</h1>
    <p>Deployed via GitHub Actions</p>
</body>
</html>
HTML_EOF
        ;;
    
    nodejs)
        cat > "example-nodejs-app/package.json" << 'JSON_EOF'
{
  "name": "nodejs-app",
  "version": "1.0.0",
  "description": "Node.js application",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "test": "echo \"No tests specified\" && exit 0"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
JSON_EOF
        
        cat > "example-nodejs-app/app.js" << 'JS_EOF'
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.json({
        status: 'success',
        message: 'Node.js Application Running',
        timestamp: new Date().toISOString()
    });
});

app.get('/api/health', (req, res) => {
    res.json({ status: 'healthy' });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
JS_EOF
        ;;
    
    python)
        cat > "example-python-app/requirements.txt" << 'REQ_EOF'
Flask==3.0.0
gunicorn==21.2.0
REQ_EOF
        
        cat > "example-python-app/app.py" << 'PY_EOF'
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'success',
        'message': 'Python/Flask Application Running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
PY_EOF
        ;;
    
    react)
        cat > "example-react-app/package.json" << 'JSON_EOF'
{
  "name": "react-app",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test --passWithNoTests",
    "eject": "react-scripts eject"
  }
}
JSON_EOF
        
        mkdir -p "example-react-app/public"
        mkdir -p "example-react-app/src"
        
        cat > "example-react-app/public/index.html" << 'HTML_EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>React App</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>
HTML_EOF
        
        cat > "example-react-app/src/index.js" << 'JS_EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
JS_EOF
        
        cat > "example-react-app/src/App.js" << 'JS_EOF'
import React from 'react';

function App() {
  return (
    <div>
      <h1>React Application</h1>
      <p>Deployed via GitHub Actions</p>
    </div>
  );
}

export default App;
JS_EOF
        ;;
esac

# Create README
cat > README.md << EOF
# ${APP_NAME}

${APP_TYPE_NAME} application deployed to AWS Lightsail via GitHub Actions.

## Deployment

This repository is configured for automatic deployment to AWS Lightsail.

### Prerequisites

1. AWS IAM Role configured for GitHub Actions OIDC
2. GitHub repository variables set:
   - \`AWS_ROLE_ARN\`: ${AWS_ROLE_ARN}

### Setup GitHub Variables

1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **Variables** tab → **New repository variable**
3. Add:
   - Name: \`AWS_ROLE_ARN\`
   - Value: \`${AWS_ROLE_ARN}\`

### Deployment Configuration

Edit \`deployment-${APP_TYPE}.config.yml\` to customize:
- Instance name and region
- Dependencies
- Deployment directory
- Post-deployment commands

### Manual Deployment

Trigger deployment manually:
1. Go to **Actions** tab
2. Select "${APP_TYPE_NAME} Deployment" workflow
3. Click **Run workflow**

## Application Structure

\`\`\`
example-${APP_TYPE}-app/     # Application code
deployment-${APP_TYPE}.config.yml  # Deployment configuration
.github/workflows/           # GitHub Actions workflows
\`\`\`

## Troubleshooting

Use the troubleshooting tools from the main deployment repository:
https://github.com/naveenraj44125-creator/lamp-stack-lightsail/tree/main/troubleshooting-tools/${APP_TYPE}

## Instance Details

- **Name**: ${INSTANCE_NAME}
- **Region**: ${AWS_REGION}
- **Type**: ${APP_TYPE_NAME}
- **Dependencies**: ${DEPENDENCIES}
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
venv/
__pycache__/

# Build outputs
build/
dist/
*.tar.gz

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
EOF

# Initialize git
git init
git add .
git commit -m "Initial commit: ${APP_TYPE_NAME} application setup"

echo ""
echo -e "${GREEN}Creating GitHub repository...${NC}"

# Create GitHub repository
gh repo create "$REPO_NAME" $VISIBILITY --source=. --remote=origin --description="$REPO_DESC"

echo ""
echo -e "${GREEN}Setting up GitHub variables...${NC}"

# Set GitHub variables
gh variable set AWS_ROLE_ARN --body "$AWS_ROLE_ARN"

echo ""
echo -e "${GREEN}Pushing code to GitHub...${NC}"

# Push to GitHub
git push -u origin main

# Clean up
cd - > /dev/null
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✓ Repository Setup Complete!                            ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${BLUE}Repository URL:${NC} $(gh repo view --json url -q .url)"
echo -e "${BLUE}Actions URL:${NC} $(gh repo view --json url -q .url)/actions"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Review the generated files in your repository"
echo "2. Customize example-${APP_TYPE}-app/ with your application code"
echo "3. Push changes to trigger automatic deployment"
echo "4. Monitor deployment in GitHub Actions"
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"
