#!/bin/bash

# Setup GitHub Actions OIDC with AWS
# This script automates the creation of OIDC provider and IAM role

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}GitHub Actions OIDC Setup for AWS${NC}\n"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq is not installed. Install it for better output formatting${NC}"
    echo "macOS: brew install jq"
fi

# Get inputs
echo -e "${YELLOW}Enter your GitHub repository (format: owner/repo):${NC}"
read -r GITHUB_REPO

echo -e "${YELLOW}Enter IAM role name (default: GitHubActionsRole):${NC}"
read -r ROLE_NAME
ROLE_NAME=${ROLE_NAME:-GitHubActionsRole}

echo -e "${YELLOW}Enter AWS region (default: us-east-1):${NC}"
read -r AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

echo -e "${YELLOW}Choose trust scope:${NC}"
echo "1) Any branch (repo:$GITHUB_REPO:*)"
echo "2) Main branch only (repo:$GITHUB_REPO:ref:refs/heads/main)"
echo "3) Production environment (repo:$GITHUB_REPO:environment:production)"
read -r TRUST_CHOICE

case $TRUST_CHOICE in
    1) TRUST_CONDITION="repo:$GITHUB_REPO:*" ;;
    2) TRUST_CONDITION="repo:$GITHUB_REPO:ref:refs/heads/main" ;;
    3) TRUST_CONDITION="repo:$GITHUB_REPO:environment:production" ;;
    *) TRUST_CONDITION="repo:$GITHUB_REPO:*" ;;
esac

# Get AWS account ID
echo -e "\n${GREEN}Getting AWS account ID...${NC}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account ID: $AWS_ACCOUNT_ID"

# Step 1: Create OIDC Provider (if it doesn't exist)
echo -e "\n${GREEN}Step 1: Creating OIDC Identity Provider...${NC}"
OIDC_PROVIDER_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"

if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN" &> /dev/null; then
    echo -e "${YELLOW}OIDC provider already exists${NC}"
else
    aws iam create-open-id-connect-provider \
        --url https://token.actions.githubusercontent.com \
        --client-id-list sts.amazonaws.com \
        --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
        --tags Key=ManagedBy,Value=github-oidc-setup
    echo -e "${GREEN}✓ OIDC provider created${NC}"
fi

# Step 2: Create trust policy
echo -e "\n${GREEN}Step 2: Creating trust policy...${NC}"
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

echo "$TRUST_POLICY" > /tmp/trust-policy.json
echo -e "${GREEN}✓ Trust policy created${NC}"

# Step 3: Create IAM role
echo -e "\n${GREEN}Step 3: Creating IAM role...${NC}"
if aws iam get-role --role-name "$ROLE_NAME" &> /dev/null; then
    echo -e "${YELLOW}Role already exists. Updating trust policy...${NC}"
    aws iam update-assume-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-document file:///tmp/trust-policy.json
else
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document file:///tmp/trust-policy.json \
        --description "Role for GitHub Actions OIDC" \
        --tags Key=ManagedBy,Value=github-oidc-setup
    echo -e "${GREEN}✓ IAM role created${NC}"
fi

ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"

# Step 4: Attach policies
echo -e "\n${GREEN}Step 4: Attaching IAM policies...${NC}"

# Attach ReadOnlyAccess
echo "Attaching ReadOnlyAccess policy..."
aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
echo -e "${GREEN}✓ Attached ReadOnlyAccess${NC}"

# Create and attach Lightsail policy
echo "Creating Lightsail full access policy..."
LIGHTSAIL_POLICY_NAME="${ROLE_NAME}-LightsailAccess"

LIGHTSAIL_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "lightsail:*",
      "Resource": "*"
    }
  ]
}
EOF
)

# Check if policy already exists
POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${LIGHTSAIL_POLICY_NAME}"
if aws iam get-policy --policy-arn "$POLICY_ARN" &> /dev/null; then
    echo -e "${YELLOW}Lightsail policy already exists${NC}"
else
    aws iam create-policy \
        --policy-name "$LIGHTSAIL_POLICY_NAME" \
        --policy-document "$LIGHTSAIL_POLICY" \
        --description "Full access to AWS Lightsail for GitHub Actions" \
        --tags Key=ManagedBy,Value=github-oidc-setup
    echo -e "${GREEN}✓ Created Lightsail policy${NC}"
fi

# Attach the Lightsail policy
aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "$POLICY_ARN"
echo -e "${GREEN}✓ Attached Lightsail policy${NC}"

# Step 5: Generate workflow example
echo -e "\n${GREEN}Step 5: Generating GitHub workflow example...${NC}"
WORKFLOW_FILE=".github/workflows/aws-deploy.yml"
mkdir -p .github/workflows

cat > "$WORKFLOW_FILE" <<EOF
name: Deploy to AWS

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  id-token: write   # Required for OIDC
  contents: read    # Required to checkout code

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: $ROLE_ARN
          aws-region: $AWS_REGION
      
      - name: Verify AWS access
        run: |
          echo "Testing AWS authentication..."
          aws sts get-caller-identity
          echo "✓ Successfully authenticated to AWS"
      
      # Add your deployment steps below
      # Example:
      # - name: Deploy to S3
      #   run: aws s3 sync ./build s3://your-bucket-name
EOF

echo -e "${GREEN}✓ Workflow file created: $WORKFLOW_FILE${NC}"

# Cleanup
rm /tmp/trust-policy.json

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo -e "Role ARN: ${YELLOW}$ROLE_ARN${NC}"
echo -e "Region: ${YELLOW}$AWS_REGION${NC}"
echo -e "Trust Condition: ${YELLOW}$TRUST_CONDITION${NC}"
echo -e "Workflow File: ${YELLOW}$WORKFLOW_FILE${NC}"
echo -e "\n${GREEN}Next Steps:${NC}"
echo "1. Review and commit the workflow file: $WORKFLOW_FILE"
echo "2. Push to GitHub and check the Actions tab"
echo "3. Add deployment steps to the workflow as needed"
echo -e "\n${YELLOW}Note: You may need to attach additional IAM policies to the role${NC}"
echo "View role in AWS Console: https://console.aws.amazon.com/iam/home#/roles/$ROLE_NAME"
