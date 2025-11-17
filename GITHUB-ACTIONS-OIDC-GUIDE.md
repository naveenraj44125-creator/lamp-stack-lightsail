# GitHub Actions OIDC Authentication Guide

Complete guide for setting up and using OpenID Connect (OIDC) authentication between GitHub Actions and AWS, eliminating the need for long-lived AWS credentials.

## Table of Contents
- [Overview](#overview)
- [What Changed](#what-changed)
- [Setup Instructions](#setup-instructions)
- [Workflow Configuration](#workflow-configuration)
- [Benefits](#benefits)
- [Troubleshooting](#troubleshooting)

## Overview

OIDC allows GitHub Actions to authenticate to AWS using short-lived tokens instead of storing AWS access keys. This provides better security, easier credential management, and improved audit trails.

### How It Works
1. GitHub generates a JWT token when workflow runs
2. Workflow exchanges token with AWS STS
3. AWS validates token against OIDC provider
4. AWS returns temporary credentials (~1 hour)
5. Workflow uses credentials to access AWS services

## What Changed

### ✅ AWS Setup (Completed)
- Created OIDC Identity Provider in AWS IAM
- Created IAM Role: `GitHubActionsRole`
- Attached Policies:
  - `ReadOnlyAccess` - Read access to all AWS services
  - `GitHubActionsRole-LightsailAccess` - Full Lightsail permissions
- Trust Policy: Only allows authentication from `main` branch

### ✅ Workflow Updates (Completed)

#### 1. `.github/workflows/deploy-generic.yml`
**Before:**
```yaml
secrets:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

**After:**
```yaml
permissions:
  id-token: write   # Required for OIDC
  contents: read
# No secrets needed!
```

#### 2. `.github/workflows/deploy-generic-reusable.yml`
**Before:**
```yaml
secrets:
  AWS_ACCESS_KEY_ID:
    required: true
  AWS_SECRET_ACCESS_KEY:
    required: true

# In each job:
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1
```

**After:**
```yaml
permissions:
  id-token: write
  contents: read
# No secrets section!

# In each job:
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::257429339749:role/GitHubActionsRole
    aws-region: us-east-1
```

## Benefits

✅ **No More Stored Credentials**: AWS access keys removed from GitHub secrets
✅ **Short-Lived Tokens**: Credentials expire automatically after ~1 hour
✅ **Better Security**: Only main branch can deploy
✅ **Audit Trail**: CloudTrail shows which workflow accessed AWS
✅ **Fine-Grained Control**: Can restrict by branch, environment, or PR

## What You Can Do Now

1. **Remove Old Secrets** (Optional but recommended):
   - Go to GitHub repo → Settings → Secrets and variables → Actions
   - Delete `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

2. **Test the Workflow**:
   ```bash
   git add .github/workflows/
   git commit -m "Migrate to OIDC authentication"
   git push origin main
   ```

3. **Monitor First Run**:
   - Go to Actions tab in GitHub
   - Watch the workflow authenticate with OIDC
   - Check for "Configure AWS credentials" step success

## AWS Resources Created

- **OIDC Provider**: `arn:aws:iam::257429339749:oidc-provider/token.actions.githubusercontent.com`
- **IAM Role**: `arn:aws:iam::257429339749:role/GitHubActionsRole`
- **Custom Policy**: `arn:aws:iam::257429339749:policy/GitHubActionsRole-LightsailAccess`

## View in AWS Console

- [IAM Role](https://console.aws.amazon.com/iam/home#/roles/GitHubActionsRole)
- [OIDC Provider](https://console.aws.amazon.com/iam/home#/providers)

## Setup Instructions

### Automated Setup (Recommended)

Use the provided setup script to automate the entire process:

```bash
chmod +x setup-github-oidc.sh
./setup-github-oidc.sh
```

The script will:
1. Create OIDC provider in AWS IAM
2. Create IAM role with trust policy
3. Attach necessary permissions
4. Generate workflow example

### Manual Setup

#### Step 1: Create OIDC Provider in AWS

1. Go to AWS IAM Console → **Identity providers**
2. Click **Add provider**
3. Select **OpenID Connect**
4. Enter:
   - **Provider URL**: `https://token.actions.githubusercontent.com`
   - Click **Get thumbprint**
   - **Audience**: `sts.amazonaws.com`
5. Click **Add provider**

#### Step 2: Create IAM Role

1. Go to IAM Console → **Roles** → **Create role**
2. Select **Web identity**
3. Choose:
   - **Identity provider**: `token.actions.githubusercontent.com`
   - **Audience**: `sts.amazonaws.com`
4. Attach policies (ReadOnlyAccess, custom Lightsail policy)
5. Name the role: `GitHubActionsRole`

#### Step 3: Configure Trust Policy

Edit the role's trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:OWNER/REPO:ref:refs/heads/main"
      }
    }
  }]
}
```

Replace:
- `ACCOUNT_ID` with your AWS account ID
- `OWNER/REPO` with your GitHub repository

## Workflow Configuration

### Basic Workflow Structure

All workflows using OIDC must include:

```yaml
name: Deploy Application

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
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::257429339749:role/GitHubActionsRole
          aws-region: us-east-1
      
      - name: Deploy
        run: |
          aws sts get-caller-identity
          # Your deployment commands here
```

### Reusable Workflow Pattern

For reusable workflows, add permissions at the top level:

```yaml
name: Reusable Deployment

on:
  workflow_call:
    inputs:
      config_file:
        required: true
        type: string

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::257429339749:role/GitHubActionsRole
          aws-region: us-east-1
```

### Calling Reusable Workflows

When calling reusable workflows, no secrets needed:

```yaml
name: Deploy App

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    uses: ./.github/workflows/deploy-reusable.yml
    with:
      config_file: 'deployment.config.yml'
    # No secrets section needed!
```

### Multiple Jobs Pattern

Each job that needs AWS access must configure credentials:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::257429339749:role/GitHubActionsRole
          aws-region: us-east-1
      
      - name: Build and push to ECR
        run: |
          aws ecr get-login-password | docker login ...
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::257429339749:role/GitHubActionsRole
          aws-region: us-east-1
      
      - name: Deploy to Lightsail
        run: |
          aws lightsail ...
```

### Trust Policy Variations

**Allow only main branch:**
```json
"token.actions.githubusercontent.com:sub": "repo:owner/repo:ref:refs/heads/main"
```

**Allow specific environment:**
```json
"token.actions.githubusercontent.com:sub": "repo:owner/repo:environment:production"
```

**Allow any branch:**
```json
"token.actions.githubusercontent.com:sub": "repo:owner/repo:*"
```

**Allow pull requests:**
```json
"token.actions.githubusercontent.com:sub": "repo:owner/repo:pull_request"
```

## Troubleshooting

### Common Issues

#### Authentication Fails

**Error**: `Not authorized to perform sts:AssumeRoleWithWebIdentity`

**Solutions**:
- Verify trust policy has correct repository name
- Check OIDC provider exists in AWS
- Ensure `permissions: id-token: write` is in workflow
- Confirm role ARN is correct

#### Missing Permissions

**Error**: `User is not authorized to perform: lightsail:GetInstance`

**Solutions**:
- Check IAM policies attached to role
- Verify policy allows required actions
- Review CloudTrail logs for denied actions

#### Wrong Branch

**Error**: `Token audience validation failed`

**Solutions**:
- Verify workflow runs from allowed branch
- Check trust policy branch restrictions
- Update trust policy if needed

### Verification Steps

1. **Check OIDC Provider**:
   ```bash
   aws iam list-open-id-connect-providers
   ```

2. **Verify Role Trust Policy**:
   ```bash
   aws iam get-role --role-name GitHubActionsRole
   ```

3. **List Attached Policies**:
   ```bash
   aws iam list-attached-role-policies --role-name GitHubActionsRole
   ```

4. **Test in Workflow**:
   ```yaml
   - name: Test AWS Access
     run: |
       aws sts get-caller-identity
       aws lightsail get-regions
   ```

## Rollback (If Needed)

If you need to rollback to secrets:
1. Re-add AWS secrets to GitHub
2. Revert the workflow changes
3. Keep the OIDC setup for future use

## Additional Resources

- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AWS IAM OIDC Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)
