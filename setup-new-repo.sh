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

echo ""
echo -e "${BLUE}GitHub Actions OIDC Setup:${NC}"
echo "1) Use existing IAM role (provide ARN)"
echo "2) Create new IAM role with OIDC"
read -p "Choose option (1-2): " OIDC_CHOICE

if [[ "$OIDC_CHOICE" == "2" ]]; then
    SETUP_OIDC=true
    read -p "IAM role name (default: GitHubActionsRole-${REPO_NAME}): " ROLE_NAME
    ROLE_NAME=${ROLE_NAME:-GitHubActionsRole-${REPO_NAME}}
    
    echo "Trust scope:"
    echo "1) Any branch (repo:OWNER/${REPO_NAME}:*)"
    echo "2) Main branch only (repo:OWNER/${REPO_NAME}:ref:refs/heads/main)"
    read -p "Choose trust scope (1-2, default: 2): " TRUST_SCOPE
    TRUST_SCOPE=${TRUST_SCOPE:-2}
else
    SETUP_OIDC=false
    read -p "AWS IAM Role ARN for GitHub Actions: " AWS_ROLE_ARN
fi

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
echo -e "${BLUE}Database Configuration:${NC}"
echo "1) No database"
echo "2) MySQL (internal - on same instance)"
echo "3) MySQL (external - AWS RDS)"
echo "4) PostgreSQL (internal - on same instance)"
echo "5) PostgreSQL (external - AWS RDS)"
read -p "Choose database option (1-5): " DB_CHOICE

DB_TYPE="none"
DB_EXTERNAL="false"
DB_RDS_NAME=""
DB_NAME=""

case $DB_CHOICE in
    2)
        DB_TYPE="mysql"
        DB_EXTERNAL="false"
        ;;
    3)
        DB_TYPE="mysql"
        DB_EXTERNAL="true"
        read -p "RDS instance name: " DB_RDS_NAME
        read -p "Database name (default: app_db): " DB_NAME
        DB_NAME=${DB_NAME:-app_db}
        ;;
    4)
        DB_TYPE="postgresql"
        DB_EXTERNAL="false"
        ;;
    5)
        DB_TYPE="postgresql"
        DB_EXTERNAL="true"
        read -p "RDS instance name: " DB_RDS_NAME
        read -p "Database name (default: app_db): " DB_NAME
        DB_NAME=${DB_NAME:-app_db}
        ;;
esac

if [[ "$DB_TYPE" != "none" ]]; then
    DEPENDENCIES="$DEPENDENCIES,$DB_TYPE"
fi

echo ""
echo -e "${BLUE}Lightsail Bucket Configuration:${NC}"
read -p "Enable Lightsail bucket for object storage? (y/N): " ENABLE_BUCKET
ENABLE_BUCKET=${ENABLE_BUCKET:-N}

if [[ "$ENABLE_BUCKET" =~ ^[Yy]$ ]]; then
    read -p "Bucket name (default: ${INSTANCE_NAME}-bucket): " BUCKET_NAME
    BUCKET_NAME=${BUCKET_NAME:-${INSTANCE_NAME}-bucket}
    
    echo "Bucket access level:"
    echo "1) Read-only (instance can download from bucket)"
    echo "2) Read-write (instance can upload to bucket)"
    read -p "Choose access level (1-2, default: 1): " BUCKET_ACCESS_CHOICE
    BUCKET_ACCESS_CHOICE=${BUCKET_ACCESS_CHOICE:-1}
    
    if [[ "$BUCKET_ACCESS_CHOICE" == "2" ]]; then
        BUCKET_ACCESS="read_write"
    else
        BUCKET_ACCESS="read_only"
    fi
    
    echo "Bucket size:"
    echo "1) Small (250GB storage, 100GB transfer/month)"
    echo "2) Medium (500GB storage, 250GB transfer/month)"
    echo "3) Large (1TB storage, 500GB transfer/month)"
    read -p "Choose bucket size (1-3, default: 1): " BUCKET_SIZE_CHOICE
    BUCKET_SIZE_CHOICE=${BUCKET_SIZE_CHOICE:-1}
    
    case $BUCKET_SIZE_CHOICE in
        2) BUCKET_BUNDLE="medium_1_0" ;;
        3) BUCKET_BUNDLE="large_1_0" ;;
        *) BUCKET_BUNDLE="small_1_0" ;;
    esac
fi

echo ""
echo -e "${BLUE}Additional Dependencies:${NC}"
read -p "Enable Redis cache? (y/N): " ENABLE_REDIS
if [[ "$ENABLE_REDIS" =~ ^[Yy]$ ]]; then
    DEPENDENCIES="$DEPENDENCIES,redis"
fi

read -p "Enable Git? (Y/n): " ENABLE_GIT
ENABLE_GIT=${ENABLE_GIT:-Y}
if [[ "$ENABLE_GIT" =~ ^[Yy]$ ]]; then
    DEPENDENCIES="$DEPENDENCIES,git"
fi

read -p "Enable SSL certificates (Let's Encrypt)? (y/N): " ENABLE_SSL
ENABLE_SSL=${ENABLE_SSL:-N}

echo ""
echo -e "${YELLOW}Summary:${NC}"
echo "Repository: $REPO_NAME"
echo "Application: $APP_NAME ($APP_TYPE_NAME)"
echo "Instance: $INSTANCE_NAME"
echo "Region: $AWS_REGION"
echo "Dependencies: $DEPENDENCIES"
if [[ "$DB_TYPE" != "none" ]]; then
    echo "Database: $DB_TYPE ($([ "$DB_EXTERNAL" = "true" ] && echo "external RDS" || echo "internal"))"
    [[ "$DB_EXTERNAL" = "true" ]] && echo "  RDS Instance: $DB_RDS_NAME"
    [[ "$DB_EXTERNAL" = "true" ]] && echo "  Database Name: $DB_NAME"
fi
if [[ "$SETUP_OIDC" == "true" ]]; then
    echo "OIDC: Will create new IAM role ($ROLE_NAME)"
else
    echo "OIDC: Using existing role"
    echo "  Role ARN: $AWS_ROLE_ARN"
fi
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
  
  # Environment variables
  environment_variables:
    APP_ENV: production
    APP_DEBUG: false
    APP_NAME: "${APP_NAME}"

aws:
  region: "${AWS_REGION}"

lightsail:
  instance_name: "${INSTANCE_NAME}"
  static_ip: ""  # Will be assigned automatically
  
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
    
    # Skip database dependencies - they'll be added separately
    if [[ "$dep" == "mysql" ]] || [[ "$dep" == "postgresql" ]]; then
        continue
    fi
    
    case $dep in
        apache)
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  apache:
    enabled: true
    version: "latest"
    config:
      document_root: "/var/www/html"
      enable_ssl: false
      enable_rewrite: true
EOF
            ;;
        nginx)
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  nginx:
    enabled: true
    version: "latest"
    config:
      document_root: "/var/www/html"
      enable_ssl: false
EOF
            ;;
        php)
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  php:
    enabled: true
    version: "8.3"
    config:
      extensions:
        - "curl"
        - "mbstring"
        - "xml"
        - "zip"
EOF
            [[ "$DB_TYPE" == "mysql" ]] && echo "        - \"mysql\"" >> "deployment-${APP_TYPE}.config.yml"
            [[ "$DB_TYPE" == "postgresql" ]] && echo "        - \"pgsql\"" >> "deployment-${APP_TYPE}.config.yml"
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
      enable_composer: true
EOF
            ;;
        nodejs)
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  nodejs:
    enabled: true
    version: "18"
    config:
      npm_packages:
        - "express"
      package_manager: "npm"
EOF
            ;;
        pm2)
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  pm2:
    enabled: true
EOF
            ;;
        python)
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  python:
    enabled: true
    version: "3.9"
    config:
      pip_packages:
        - "flask"
        - "gunicorn"
      virtual_env: true
EOF
            ;;
        redis)
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  redis:
    enabled: true
    version: "latest"
    config:
      bind_all_interfaces: false
EOF
            ;;
        git)
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  git:
    enabled: true
    config:
      install_lfs: false
EOF
            ;;
    esac
done

# Add database configuration
if [[ "$DB_TYPE" != "none" ]]; then
    cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  
  # Database Configuration
  ${DB_TYPE}:
    enabled: true
    external: ${DB_EXTERNAL}
EOF
    
    if [[ "$DB_EXTERNAL" == "true" ]]; then
        cat >> "deployment-${APP_TYPE}.config.yml" << EOF
    rds:
      database_name: "${DB_RDS_NAME}"
      region: "${AWS_REGION}"
      master_database: "${DB_NAME}"
      environment:
        DB_CONNECTION_TIMEOUT: "30"
        DB_CHARSET: "utf8mb4"
EOF
    fi
fi

# Add SSL configuration if enabled
if [[ "$ENABLE_SSL" =~ ^[Yy]$ ]]; then
    cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  
  ssl_certificates:
    enabled: true
    config:
      provider: "letsencrypt"
      domains: []  # Add your domains here
EOF
fi

# Add firewall configuration
cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  
  firewall:
    enabled: true
    config:
      allowed_ports:
        - "22"    # SSH
        - "80"    # HTTP
        - "443"   # HTTPS
      deny_all_other: true

# Deployment Configuration
deployment:
  target_directory: "/var/www/${APP_TYPE}-app"
  
  # Timeout settings (in seconds)
  timeouts:
    ssh_connection: 120
    command_execution: 300
    health_check: 180
  
  # Retry settings
  retries:
    max_attempts: 3
    ssh_connection: 5
  
  # Post-deployment commands (optional)
  post_deploy_commands: []
  
  # Deployment steps
  steps:
    pre_deployment:
      common:
        enabled: true
        update_packages: true
        create_directories: true
        backup_enabled: true
      dependencies:
        enabled: true
        install_system_deps: true
        configure_services: true
    
    post_deployment:
      common:
        enabled: true
        verify_extraction: true
        create_env_file: true
        cleanup_temp_files: true
      dependencies:
        enabled: true
        configure_application: true
        set_permissions: true
        restart_services: true
        optimize_performance: true
    
    verification:
      enabled: true
      health_check: true
      external_connectivity: true
      endpoints_to_test:
        - "/"

# GitHub Actions Configuration
github_actions:
  triggers:
    push_branches:
      - main
    workflow_dispatch: true
  
  jobs:
    test:
      enabled: true
      language_specific_tests: true

# Monitoring and Logging
monitoring:
  health_check:
    endpoint: "/"
    expected_content: ""
    max_attempts: 10
    wait_between_attempts: 10
    initial_wait: 30
  
  logging:
    level: INFO
    include_timestamps: true

# Security Configuration
security:
  file_permissions:
    web_files: "644"
    directories: "755"
    config_files: "600"
  
  web_server:
    hide_version: true
    disable_server_tokens: true
    enable_security_headers: true

# Backup Configuration
backup:
  enabled: true
  retention_days: 7
  backup_location: "/var/backups/deployments"
  include_database: false
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
if [[ "$SETUP_OIDC" == "true" ]]; then
    echo -e "${GREEN}Setting up OIDC and IAM role...${NC}"
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Could not get AWS account ID. Make sure AWS credentials are configured.${NC}"
        echo "Run: source .aws-creds.sh"
        exit 1
    fi
    
    GITHUB_OWNER=$(gh api user -q .login)
    GITHUB_REPO="${GITHUB_OWNER}/${REPO_NAME}"
    
    # Set trust condition based on choice
    if [[ "$TRUST_SCOPE" == "1" ]]; then
        TRUST_CONDITION="repo:${GITHUB_REPO}:*"
    else
        TRUST_CONDITION="repo:${GITHUB_REPO}:ref:refs/heads/main"
    fi
    
    # Create OIDC Provider (if it doesn't exist)
    OIDC_PROVIDER_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
    
    if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN" &> /dev/null; then
        echo "✓ OIDC provider already exists"
    else
        aws iam create-open-id-connect-provider \
            --url https://token.actions.githubusercontent.com \
            --client-id-list sts.amazonaws.com \
            --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
            --tags Key=ManagedBy,Value=setup-new-repo > /dev/null
        echo "✓ OIDC provider created"
    fi
    
    # Create trust policy
    TRUST_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "$OIDC_PROVIDER_ARN"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "$TRUST_CONDITION"
        }
      }
    }
  ]
}
EOF
)
    
    echo "$TRUST_POLICY" > /tmp/trust-policy-${REPO_NAME}.json
    
    # Create or update IAM role
    if aws iam get-role --role-name "$ROLE_NAME" &> /dev/null; then
        echo "✓ Role exists, updating trust policy..."
        aws iam update-assume-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-document file:///tmp/trust-policy-${REPO_NAME}.json > /dev/null
    else
        aws iam create-role \
            --role-name "$ROLE_NAME" \
            --assume-role-policy-document file:///tmp/trust-policy-${REPO_NAME}.json \
            --description "Role for GitHub Actions OIDC - ${REPO_NAME}" \
            --max-session-duration 3600 \
            --tags Key=ManagedBy,Value=setup-new-repo Key=Repository,Value=${REPO_NAME} > /dev/null
        echo "✓ IAM role created"
        
        # Attach policies
        echo "✓ Attaching IAM policies..."
        aws iam attach-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess > /dev/null
        
        # Create Lightsail policy
        LIGHTSAIL_POLICY_NAME="${ROLE_NAME}-LightsailAccess"
        POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${LIGHTSAIL_POLICY_NAME}"
        
        if ! aws iam get-policy --policy-arn "$POLICY_ARN" &> /dev/null; then
            LIGHTSAIL_POLICY='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"lightsail:*","Resource":"*"}]}'
            aws iam create-policy \
                --policy-name "$LIGHTSAIL_POLICY_NAME" \
                --policy-document "$LIGHTSAIL_POLICY" \
                --description "Full access to AWS Lightsail" \
                --tags Key=ManagedBy,Value=setup-new-repo > /dev/null
        fi
        
        aws iam attach-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-arn "$POLICY_ARN" > /dev/null
        echo "✓ Lightsail policy attached"
    fi
    
    AWS_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
    
    # Cleanup
    rm /tmp/trust-policy-${REPO_NAME}.json
    
    echo "✓ OIDC setup complete"
fi

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
echo -e "${BLUE}Repository URL:${NC} https://github.com/$(gh api user -q .login)/${REPO_NAME}"
echo -e "${BLUE}Actions URL:${NC} https://github.com/$(gh api user -q .login)/${REPO_NAME}/actions"
echo ""
if [[ "$SETUP_OIDC" == "true" ]]; then
    echo -e "${BLUE}IAM Role ARN:${NC} ${AWS_ROLE_ARN}"
    echo -e "${BLUE}Trust Condition:${NC} ${TRUST_CONDITION}"
    echo ""
fi
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Review the generated files in your repository"
echo "2. Customize example-${APP_TYPE}-app/ with your application code"
echo "3. Push changes to trigger automatic deployment"
echo "4. Monitor deployment in GitHub Actions"
if [[ "$SETUP_OIDC" == "true" ]]; then
    echo ""
    echo -e "${GREEN}✓ OIDC is configured and ready to use!${NC}"
fi
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"
