#!/bin/bash
# Integrate Lightsail GitHub Actions into Existing Repository
# This script adds deployment automation to your existing GitHub repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Lightsail GitHub Actions Integration Script              ║${NC}"
echo -e "${BLUE}║  Add automated deployment to your existing repository      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not a git repository${NC}"
    echo "Please run this script from the root of your git repository"
    exit 1
fi

# Get repository information
REPO_URL=$(git config --get remote.origin.url || echo "")
CURRENT_BRANCH=$(git branch --show-current)

echo -e "${GREEN}✓ Git repository detected${NC}"
echo "  Repository: $REPO_URL"
echo "  Current branch: $CURRENT_BRANCH"
echo ""

# Confirm with user
read -p "Do you want to integrate Lightsail deployment into this repository? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Integration cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Step 1: Application Configuration${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Application type selection
echo "Select your application type:"
echo "1) LAMP Stack (Apache + PHP + MySQL/PostgreSQL)"
echo "2) NGINX (Static sites or reverse proxy)"
echo "3) Node.js (Express, Next.js, etc.)"
echo "4) Python (Flask, Django, FastAPI)"
echo "5) React (Create React App, Vite, etc.)"
echo "6) Docker - Basic LAMP (Apache + MySQL + Redis + phpMyAdmin)"
echo "7) Docker - Recipe Manager (Full-featured app with S3)"
read -p "Enter choice (1-7): " APP_TYPE_CHOICE

case $APP_TYPE_CHOICE in
    1) APP_TYPE="lamp"; APP_TYPE_NAME="LAMP Stack";;
    2) APP_TYPE="nginx"; APP_TYPE_NAME="NGINX";;
    3) APP_TYPE="nodejs"; APP_TYPE_NAME="Node.js";;
    4) APP_TYPE="python"; APP_TYPE_NAME="Python";;
    5) APP_TYPE="react"; APP_TYPE_NAME="React";;
    6) APP_TYPE="docker"; APP_TYPE_NAME="Docker Basic LAMP";;
    7) APP_TYPE="docker-recipe"; APP_TYPE_NAME="Docker Recipe Manager";;
    *) echo "Invalid choice"; exit 1;;
esac

echo -e "${GREEN}✓ Selected: $APP_TYPE_NAME${NC}"
echo ""

# Instance name
read -p "Enter Lightsail instance name (e.g., my-app-prod): " INSTANCE_NAME
if [ -z "$INSTANCE_NAME" ]; then
    echo -e "${RED}❌ Instance name is required${NC}"
    exit 1
fi

# AWS Region
echo ""
echo "Select AWS region:"
echo "1) us-east-1 (N. Virginia)"
echo "2) us-west-2 (Oregon)"
echo "3) eu-west-1 (Ireland)"
echo "4) ap-southeast-1 (Singapore)"
read -p "Enter choice (1-4) [default: 1]: " REGION_CHOICE
case ${REGION_CHOICE:-1} in
    1) AWS_REGION="us-east-1";;
    2) AWS_REGION="us-west-2";;
    3) AWS_REGION="eu-west-1";;
    4) AWS_REGION="ap-southeast-1";;
    *) AWS_REGION="us-east-1";;
esac

echo -e "${GREEN}✓ Region: $AWS_REGION${NC}"
echo ""

# Database configuration
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Step 2: Database Configuration${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ "$APP_TYPE" == "lamp" ]] || [[ "$APP_TYPE" == "nodejs" ]] || [[ "$APP_TYPE" == "python" ]]; then
    echo "Do you need a database?"
    echo "1) No database"
    echo "2) MySQL (local or RDS)"
    echo "3) PostgreSQL (local or RDS)"
    read -p "Enter choice (1-3): " DB_CHOICE
    
    case $DB_CHOICE in
        1) DB_TYPE="none";;
        2) DB_TYPE="mysql";;
        3) DB_TYPE="postgresql";;
        *) DB_TYPE="none";;
    esac
    
    if [[ "$DB_TYPE" != "none" ]]; then
        read -p "Use external RDS database? (y/n) [default: n]: " USE_RDS
        if [[ "$USE_RDS" =~ ^[Yy]$ ]]; then
            DB_EXTERNAL="true"
            read -p "Enter RDS instance name: " DB_RDS_NAME
            read -p "Enter database name: " DB_NAME
        else
            DB_EXTERNAL="false"
            DB_RDS_NAME=""
            DB_NAME="app_db"
        fi
    fi
else
    DB_TYPE="none"
    DB_EXTERNAL="false"
fi

echo -e "${GREEN}✓ Database configured${NC}"
echo ""

# Bucket configuration
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Step 3: S3 Bucket Configuration${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

read -p "Enable Lightsail bucket for file storage? (y/n) [default: n]: " ENABLE_BUCKET
if [[ "$ENABLE_BUCKET" =~ ^[Yy]$ ]]; then
    read -p "Enter bucket name: " BUCKET_NAME
    
    echo "Select bucket access level:"
    echo "1) read_only - Instance can only download files"
    echo "2) read_write - Instance can upload and download files"
    read -p "Enter choice (1-2) [default: 2]: " BUCKET_ACCESS_CHOICE
    case ${BUCKET_ACCESS_CHOICE:-2} in
        1) BUCKET_ACCESS="read_only";;
        2) BUCKET_ACCESS="read_write";;
        *) BUCKET_ACCESS="read_write";;
    esac
    
    echo "Select bucket size:"
    echo "1) small_1_0 - 250GB storage, 100GB transfer/month"
    echo "2) medium_1_0 - 500GB storage, 250GB transfer/month"
    echo "3) large_1_0 - 1TB storage, 500GB transfer/month"
    read -p "Enter choice (1-3) [default: 1]: " BUCKET_SIZE_CHOICE
    case ${BUCKET_SIZE_CHOICE:-1} in
        1) BUCKET_BUNDLE="small_1_0";;
        2) BUCKET_BUNDLE="medium_1_0";;
        3) BUCKET_BUNDLE="large_1_0";;
        *) BUCKET_BUNDLE="small_1_0";;
    esac
fi

echo -e "${GREEN}✓ Bucket configured${NC}"
echo ""

# OIDC Setup
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Step 4: AWS Authentication${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Do you have an existing AWS IAM role for GitHub OIDC?"
read -p "(y/n) [default: n]: " HAS_ROLE

if [[ "$HAS_ROLE" =~ ^[Yy]$ ]]; then
    SETUP_OIDC="false"
    read -p "Enter your AWS Role ARN: " AWS_ROLE_ARN
else
    SETUP_OIDC="true"
    ROLE_NAME="GitHubActionsRole-${INSTANCE_NAME}"
    echo -e "${YELLOW}⚠️  You'll need to run setup-github-oidc.sh after this script${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Configuration Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Application: $APP_TYPE_NAME"
echo "Instance: $INSTANCE_NAME"
echo "Region: $AWS_REGION"
if [[ "$DB_TYPE" != "none" ]]; then
    echo "Database: $DB_TYPE ($([ "$DB_EXTERNAL" = "true" ] && echo "external RDS" || echo "internal"))"
    [[ "$DB_EXTERNAL" = "true" ]] && echo "  RDS Instance: $DB_RDS_NAME"
    [[ "$DB_EXTERNAL" = "true" ]] && echo "  Database Name: $DB_NAME"
fi
if [[ "$ENABLE_BUCKET" =~ ^[Yy]$ ]]; then
    echo "Bucket: $BUCKET_NAME ($BUCKET_ACCESS, $BUCKET_BUNDLE)"
fi
if [[ "$SETUP_OIDC" == "true" ]]; then
    echo "OIDC: Will create new IAM role ($ROLE_NAME)"
else
    echo "OIDC: Using existing role"
    echo "  Role ARN: $AWS_ROLE_ARN"
fi
echo ""

read -p "Proceed with integration? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Integration cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Installing Deployment System${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Create directories
echo "Creating directory structure..."
mkdir -p .github/workflows
mkdir -p workflows

# Download or copy workflow files
echo "Installing workflow files..."

# Check if we're in the lamp-stack-lightsail repo
if [ -f "workflows/lightsail_common.py" ]; then
    echo "  ✓ Using local workflow files"
    SOURCE_DIR="."
else
    echo "  Downloading workflow files from GitHub..."
    REPO_URL="https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main"
    
    # Download workflow files
    curl -sL "$REPO_URL/.github/workflows/deploy-generic-reusable.yml" -o .github/workflows/deploy-generic-reusable.yml
    
    # Download Python modules
    for file in config_loader.py dependency_manager.py deploy-pre-steps-generic.py deploy-post-steps-generic.py deploy-post-steps-universal.py deployment_monitor.py lightsail_common.py lightsail_rds.py lightsail_bucket.py view_command_log.py; do
        curl -sL "$REPO_URL/workflows/$file" -o "workflows/$file"
    done
    
    # Download OIDC setup script if needed
    if [[ "$SETUP_OIDC" == "true" ]]; then
        echo "  Downloading OIDC setup script..."
        curl -sL "$REPO_URL/setup-github-oidc.sh" -o setup-github-oidc.sh
        chmod +x setup-github-oidc.sh
    fi
    
    SOURCE_DIR="."
fi

# Create deployment config
echo "Creating deployment configuration..."
cat > "deployment-${APP_TYPE}.config.yml" << EOF
# Deployment Configuration for $APP_TYPE_NAME
# Generated by integrate-lightsail-actions.sh

# AWS Configuration
aws:
  region: $AWS_REGION

# Lightsail Instance Configuration
lightsail:
  instance_name: $INSTANCE_NAME
  static_ip: ""  # Will be assigned automatically
  
  # Instance will be auto-created if it doesn't exist
  auto_create: true
  blueprint_id: "ubuntu_22_04"
  bundle_id: "nano_3_0"  # 512 MB RAM, 1 vCPU, 20 GB SSD
EOF

# Add bucket configuration if enabled
if [[ "$ENABLE_BUCKET" =~ ^[Yy]$ ]]; then
    cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  
  # Lightsail Bucket Configuration
  bucket:
    enabled: true
    name: "$BUCKET_NAME"
    access_level: "$BUCKET_ACCESS"
    bundle_id: "$BUCKET_BUNDLE"
EOF
fi

# Add application configuration based on type
cat >> "deployment-${APP_TYPE}.config.yml" << 'EOF'

# Application Configuration
application:
  name: my-app
  version: "1.0.0"
  type: web
  
  # Files to include in deployment package
  package_files:
EOF

# Add package files based on app type
case $APP_TYPE in
    lamp)
        cat >> "deployment-${APP_TYPE}.config.yml" << 'EOF'
    - "*.php"
    - "css/"
    - "js/"
    - "config/"
    - "assets/"
EOF
        ;;
    nginx)
        cat >> "deployment-${APP_TYPE}.config.yml" << 'EOF'
    - "*.html"
    - "css/"
    - "js/"
    - "assets/"
    - "images/"
EOF
        ;;
    nodejs)
        cat >> "deployment-${APP_TYPE}.config.yml" << 'EOF'
    - "package.json"
    - "package-lock.json"
    - "*.js"
    - "src/"
    - "public/"
EOF
        ;;
    python)
        cat >> "deployment-${APP_TYPE}.config.yml" << 'EOF'
    - "requirements.txt"
    - "*.py"
    - "app/"
    - "static/"
    - "templates/"
EOF
        ;;
    react)
        cat >> "deployment-${APP_TYPE}.config.yml" << 'EOF'
    - "build/"
    - "package.json"
EOF
        ;;
esac

# Add dependencies configuration
cat >> "deployment-${APP_TYPE}.config.yml" << EOF

  package_fallback: true
  
  environment_variables:
    APP_ENV: production
    APP_DEBUG: false

# Dependencies Configuration
dependencies:
EOF

# Add dependencies based on app type
case $APP_TYPE in
    lamp)
        cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  apache:
    enabled: true
    version: "latest"
    config:
      document_root: "/var/www/html"
      enable_ssl: false
      enable_rewrite: true
  
  php:
    enabled: true
    version: "8.3"
    config:
      extensions:
        - "pgsql"
        - "curl"
        - "mbstring"
        - "xml"
        - "zip"
      enable_composer: true
  
  $DB_TYPE:
    enabled: $([ "$DB_TYPE" != "none" ] && echo "true" || echo "false")
    external: $DB_EXTERNAL
EOF
        if [[ "$DB_EXTERNAL" == "true" ]]; then
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
    rds:
      database_name: "$DB_RDS_NAME"
      region: "$AWS_REGION"
      master_database: "$DB_NAME"
EOF
        fi
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
    
    nodejs)
        cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  nodejs:
    enabled: true
    version: "18"
    config:
      npm_packages:
        - "pm2"
      package_manager: "npm"
  
  $DB_TYPE:
    enabled: $([ "$DB_TYPE" != "none" ] && echo "true" || echo "false")
    external: $DB_EXTERNAL
EOF
        if [[ "$DB_EXTERNAL" == "true" ]]; then
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
    rds:
      database_name: "$DB_RDS_NAME"
      region: "$AWS_REGION"
      master_database: "$DB_NAME"
EOF
        fi
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
  
  $DB_TYPE:
    enabled: $([ "$DB_TYPE" != "none" ] && echo "true" || echo "false")
    external: $DB_EXTERNAL
EOF
        if [[ "$DB_EXTERNAL" == "true" ]]; then
            cat >> "deployment-${APP_TYPE}.config.yml" << EOF
    rds:
      database_name: "$DB_RDS_NAME"
      region: "$AWS_REGION"
      master_database: "$DB_NAME"
EOF
        fi
        ;;
    
    react)
        cat >> "deployment-${APP_TYPE}.config.yml" << EOF
  nginx:
    enabled: true
    version: "latest"
    config:
      document_root: "/var/www/html"
      enable_ssl: false
  
  nodejs:
    enabled: true
    version: "18"
    config:
      npm_packages: []
      package_manager: "npm"
EOF
        ;;
esac

# Add common dependencies
cat >> "deployment-${APP_TYPE}.config.yml" << 'EOF'
  
  git:
    enabled: true
    config:
      install_lfs: false
  
  firewall:
    enabled: true
    config:
      allowed_ports:
        - "22"
        - "80"
        - "443"
      deny_all_other: true

# Deployment Configuration
deployment:
  timeouts:
    ssh_connection: 120
    command_execution: 300
    health_check: 180
  
  retries:
    max_attempts: 3
    ssh_connection: 5

# GitHub Actions Configuration
github_actions:
  triggers:
    push_branches:
      - main
      - master
    workflow_dispatch: true
  
  jobs:
    test:
      enabled: true
    deployment:
      deploy_on_push: true
      deploy_on_pr: false

# Monitoring and Logging
monitoring:
  health_check:
    endpoint: "/"
    expected_content: ""
    max_attempts: 10
    wait_between_attempts: 10
    initial_wait: 30
EOF

echo "  ✓ Created deployment-${APP_TYPE}.config.yml"

# Create GitHub Actions workflow
echo "Creating GitHub Actions workflow..."
cat > .github/workflows/deploy-to-lightsail.yml << EOF
name: Deploy to AWS Lightsail

on:
  push:
    branches: [main, master]
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    uses: ./.github/workflows/deploy-generic-reusable.yml
    with:
      config_file: 'deployment-${APP_TYPE}.config.yml'
      aws_region: '$AWS_REGION'
    secrets:
      aws_role_arn: \${{ vars.AWS_ROLE_ARN || secrets.AWS_ROLE_ARN }}
EOF

echo "  ✓ Created .github/workflows/deploy-to-lightsail.yml"

# Create README
echo "Creating integration README..."
cat > LIGHTSAIL-DEPLOYMENT.md << EOF
# Lightsail Deployment Integration

This repository has been integrated with AWS Lightsail automated deployment.

## Configuration

- **Application Type**: $APP_TYPE_NAME
- **Instance Name**: $INSTANCE_NAME
- **AWS Region**: $AWS_REGION
$([ "$DB_TYPE" != "none" ] && echo "- **Database**: $DB_TYPE ($([ "$DB_EXTERNAL" = "true" ] && echo "external RDS" || echo "internal"))")
$([ "$DB_EXTERNAL" = "true" ] && echo "- **RDS Instance**: $DB_RDS_NAME")
$([ "$ENABLE_BUCKET" =~ ^[Yy]$ ] && echo "- **Bucket**: $BUCKET_NAME ($BUCKET_ACCESS)")

## Setup Steps

### 1. Configure AWS Authentication

$(if [[ "$SETUP_OIDC" == "true" ]]; then
    echo "Run the OIDC setup script:"
    echo "\`\`\`bash"
    echo "./setup-github-oidc.sh"
    echo "\`\`\`"
    echo ""
    echo "This will create an IAM role: \`$ROLE_NAME\`"
else
    echo "Add your AWS Role ARN to GitHub:"
    echo "1. Go to your repository Settings → Secrets and variables → Actions"
    echo "2. Add a new variable: \`AWS_ROLE_ARN\`"
    echo "3. Value: \`$AWS_ROLE_ARN\`"
fi)

### 2. Configure Database (if applicable)

$(if [[ "$DB_EXTERNAL" == "true" ]]; then
    echo "Set up RDS database secrets in GitHub:"
    echo "1. Go to Settings → Secrets and variables → Actions"
    echo "2. Add these secrets:"
    echo "   - \`DB_USER\`: Database username"
    echo "   - \`DB_PASSWORD\`: Database password"
fi)

### 3. Deploy

Push to main branch or manually trigger the workflow:
\`\`\`bash
git add .
git commit -m "Add Lightsail deployment"
git push origin main
\`\`\`

Or use GitHub Actions UI: Actions → Deploy to AWS Lightsail → Run workflow

## Files Added

- \`.github/workflows/deploy-to-lightsail.yml\` - Main deployment workflow
- \`.github/workflows/deploy-generic-reusable.yml\` - Reusable workflow
- \`deployment-${APP_TYPE}.config.yml\` - Deployment configuration
- \`workflows/*.py\` - Deployment automation scripts

## Monitoring

Check deployment status:
- GitHub Actions tab in your repository
- Deployment logs show detailed progress
- Health checks verify successful deployment

## Customization

Edit \`deployment-${APP_TYPE}.config.yml\` to customize:
- Dependencies and versions
- Environment variables
- Deployment steps
- Health check endpoints

## Troubleshooting

If deployment fails:
1. Check GitHub Actions logs
2. Verify AWS credentials are configured
3. Ensure instance name is unique
4. Check deployment config syntax

For more help, see: https://github.com/naveenraj44125-creator/lamp-stack-lightsail
EOF

echo "  ✓ Created LIGHTSAIL-DEPLOYMENT.md"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Step 5: AWS OIDC Setup${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ "$SETUP_OIDC" == "true" ]]; then
    echo -e "${GREEN}Setting up OIDC and IAM role...${NC}"
    
    # Check if AWS CLI is configured
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS CLI is not configured${NC}"
        echo ""
        echo "Please configure AWS credentials first:"
        echo "  aws configure"
        echo ""
        echo "Or if you have a credentials script:"
        echo "  source .aws-creds.sh"
        echo ""
        echo "After configuring AWS, run this script again or manually set up OIDC:"
        echo "  ./setup-github-oidc.sh"
        echo ""
        SETUP_OIDC="false"
    else
        # Get AWS account ID
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
        
        # Get GitHub repository info
        GITHUB_OWNER=$(git config --get remote.origin.url | sed -n 's#.*/\([^/]*\)/\([^/]*\)\.git#\1#p')
        REPO_NAME=$(git config --get remote.origin.url | sed -n 's#.*/\([^/]*\)/\([^/]*\)\.git#\2#p')
        
        if [ -z "$GITHUB_OWNER" ] || [ -z "$REPO_NAME" ]; then
            echo -e "${YELLOW}⚠️  Could not detect GitHub repository info${NC}"
            read -p "Enter GitHub owner/username: " GITHUB_OWNER
            read -p "Enter repository name: " REPO_NAME
        fi
        
        GITHUB_REPO="${GITHUB_OWNER}/${REPO_NAME}"
        
        # Set trust condition (default to main branch only)
        TRUST_CONDITION="repo:${GITHUB_REPO}:ref:refs/heads/main"
        
        echo "Repository: $GITHUB_REPO"
        echo "AWS Account: $AWS_ACCOUNT_ID"
        echo "IAM Role: $ROLE_NAME"
        echo ""
        
        # Create OIDC Provider (if it doesn't exist)
        OIDC_PROVIDER_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
        
        if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN" &> /dev/null; then
            echo "✓ OIDC provider already exists"
        else
            echo "Creating OIDC provider..."
            aws iam create-open-id-connect-provider \
                --url https://token.actions.githubusercontent.com \
                --client-id-list sts.amazonaws.com \
                --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
                --tags Key=ManagedBy,Value=integrate-lightsail-actions > /dev/null
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
            echo "Creating IAM role..."
            aws iam create-role \
                --role-name "$ROLE_NAME" \
                --assume-role-policy-document file:///tmp/trust-policy-${REPO_NAME}.json \
                --description "Role for GitHub Actions OIDC - ${REPO_NAME}" \
                --tags Key=ManagedBy,Value=integrate-lightsail-actions Key=Repository,Value=${REPO_NAME} > /dev/null
            echo "✓ IAM role created"
            
            # Attach policies
            echo "Attaching IAM policies..."
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
                    --tags Key=ManagedBy,Value=integrate-lightsail-actions > /dev/null
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
        echo ""
    fi
fi

# Set GitHub variable if gh CLI is available
if command -v gh &> /dev/null && [[ -n "$AWS_ROLE_ARN" ]]; then
    echo -e "${GREEN}Setting GitHub variable...${NC}"
    if gh variable set AWS_ROLE_ARN --body "$AWS_ROLE_ARN" 2>/dev/null; then
        echo "✓ AWS_ROLE_ARN variable set in GitHub"
    else
        echo -e "${YELLOW}⚠️  Could not set GitHub variable automatically${NC}"
        echo "Please set it manually:"
        echo "  1. Go to repository Settings → Secrets and variables → Actions"
        echo "  2. Add variable: AWS_ROLE_ARN"
        echo "  3. Value: $AWS_ROLE_ARN"
    fi
else
    if [[ -n "$AWS_ROLE_ARN" ]]; then
        echo -e "${YELLOW}⚠️  GitHub CLI not available${NC}"
        echo "Please set AWS_ROLE_ARN variable manually:"
        echo "  1. Go to repository Settings → Secrets and variables → Actions"
        echo "  2. Add variable: AWS_ROLE_ARN"
        echo "  3. Value: $AWS_ROLE_ARN"
    fi
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Integration Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Files created:"
echo "  ✓ .github/workflows/deploy-to-lightsail.yml"
echo "  ✓ .github/workflows/deploy-generic-reusable.yml"
echo "  ✓ deployment-${APP_TYPE}.config.yml"
echo "  ✓ workflows/*.py (deployment modules)"
echo "  ✓ LIGHTSAIL-DEPLOYMENT.md"
echo ""

if [[ "$SETUP_OIDC" == "true" ]] && [[ -n "$AWS_ROLE_ARN" ]]; then
    echo -e "${GREEN}AWS Authentication:${NC}"
    echo "  ✓ OIDC provider configured"
    echo "  ✓ IAM role created: $ROLE_NAME"
    echo "  ✓ Role ARN: $AWS_ROLE_ARN"
    echo "  ✓ Trust condition: $TRUST_CONDITION"
    echo ""
fi

echo -e "${YELLOW}Next Steps:${NC}"
echo ""

echo "1. Review and customize deployment-${APP_TYPE}.config.yml"
echo ""

echo "2. Commit and push changes:"
echo "   ${BLUE}git add .${NC}"
echo "   ${BLUE}git commit -m \"Add Lightsail deployment automation\"${NC}"
echo "   ${BLUE}git push origin $CURRENT_BRANCH${NC}"
echo ""

echo "3. Monitor deployment in GitHub Actions tab"
echo ""

if [[ "$SETUP_OIDC" == "true" ]] && [[ -n "$AWS_ROLE_ARN" ]]; then
    echo -e "${GREEN}✓ OIDC is configured and ready to use!${NC}"
    echo ""
fi

echo -e "${GREEN}Your repository is now ready for automated Lightsail deployment! 🚀${NC}"
