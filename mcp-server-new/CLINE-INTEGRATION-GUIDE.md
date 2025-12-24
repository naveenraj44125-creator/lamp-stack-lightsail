# 🚀 Cline + MCP Server + AWS Lightsail Integration Guide

This comprehensive guide walks you through integrating the Enhanced Lightsail Deployment MCP Server with Cline IDE to enable AI-powered deployments to AWS Lightsail using GitHub Actions.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Install and Configure MCP Server](#step-1-install-and-configure-mcp-server)
4. [Step 2: Configure Cline IDE](#step-2-configure-cline-ide)
5. [Step 3: Set Up AWS for GitHub Actions](#step-3-set-up-aws-for-github-actions)
6. [Step 4: Deploy Your First Application](#step-4-deploy-your-first-application)
7. [Complete Workflow Examples](#complete-workflow-examples)
8. [Troubleshooting](#troubleshooting)
9. [Available MCP Tools Reference](#available-mcp-tools-reference)

---

## Overview

This integration enables you to:
- 🤖 Use AI (Claude via Cline) to analyze your projects and generate deployment configurations
- 🚀 Automatically deploy applications to AWS Lightsail via GitHub Actions
- 🔧 Troubleshoot deployment issues with AI-powered diagnostics
- 💰 Get cost optimization recommendations
- 🔒 Ensure security best practices

### Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Cline     │────▶│ MCP Server  │────▶│   GitHub    │────▶│   AWS       │
│   IDE       │     │ (Local)     │     │   Actions   │     │  Lightsail  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      │  Natural Language │  Tool Calls       │  Workflow         │  Deploy
      │  Commands         │  & Analysis       │  Triggers         │  & Run
```

---

## Prerequisites

Before starting, ensure you have:

### Required Software
- **Node.js 18+**: `node --version`
- **Git**: `git --version`
- **GitHub CLI**: `gh --version`
- **AWS CLI**: `aws --version`
- **Cline IDE Extension**: Install from VS Code marketplace

### Required Accounts
- **GitHub Account**: With repository creation permissions
- **AWS Account**: With Lightsail and IAM permissions

### AWS Permissions Needed
Your AWS user/role needs these permissions:
- `lightsail:*` - Full Lightsail access
- `iam:CreateRole`, `iam:AttachRolePolicy` - For GitHub OIDC setup
- `bedrock:InvokeModel` - For AI features (optional)

---

## Step 1: Install and Configure MCP Server

### 1.1 Clone the Repository

```bash
# Clone the repository
git clone https://github.com/naveenraj44125-creator/lamp-stack-lightsail.git
cd lamp-stack-lightsail/mcp-server-new

# Install dependencies
npm install
```

### 1.2 Configure AWS Credentials

Create a credentials file (or use `aws configure`):

```bash
# Option 1: Create .aws-creds.sh file
cat > ../.aws-creds.sh << 'EOF'
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
EOF

# Load credentials
source ../.aws-creds.sh
```

```bash
# Option 2: Use AWS CLI
aws configure
# Enter your Access Key ID, Secret Access Key, and region
```

### 1.3 Test the MCP Server

```bash
# Start the server
npm start

# In another terminal, test the health endpoint
curl http://localhost:3001/health
```

Expected output:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "features": ["intelligent-analysis", "cost-optimization", "security-assessment", "ai-powered-bedrock"],
  "ai": {
    "provider": "AWS Bedrock",
    "model": "anthropic.claude-3-sonnet-20240229-v1:0",
    "region": "us-east-1"
  }
}
```

---

## Step 2: Configure Cline IDE

### 2.1 Install Cline Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Cline"
4. Install the Cline extension

### 2.2 Configure MCP Server in Cline

There are two ways to use the MCP server with Cline:

---

**Option A: Stdio Transport (Recommended - Auto-starts server)**

This option automatically starts the MCP server when Cline needs it. No need to manually run the server.

1. Open VS Code Settings (Cmd+, on Mac, Ctrl+, on Windows)
2. Search for "Cline MCP" or navigate to Cline extension settings
3. Find "MCP Servers" configuration
4. Add the following configuration to your Cline MCP settings file:

**Location:** `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

Or via Cline UI: Click the MCP servers icon in Cline panel → "Configure MCP Servers"

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "node",
      "args": ["/full/path/to/lamp-stack-lightsail/mcp-server-new/server.js", "--stdio"],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "your-access-key",
        "AWS_SECRET_ACCESS_KEY": "your-secret-key"
      }
    }
  }
}
```

**Important:** 
- The `--stdio` flag is required for Cline integration (enables stdio transport mode)
- Replace `/full/path/to/` with the actual absolute path to your cloned repository

Example paths:
- macOS: `/Users/yourname/projects/lamp-stack-lightsail/mcp-server-new/server.js`
- Linux: `/home/yourname/projects/lamp-stack-lightsail/mcp-server-new/server.js`
- Windows: `C:\\Users\\yourname\\projects\\lamp-stack-lightsail\\mcp-server-new\\server.js`

---

**Option B: SSE Transport (Manual server start)**

This option requires you to manually start the MCP server first.

1. **Start the MCP server in a terminal:**
```bash
cd /path/to/lamp-stack-lightsail/mcp-server-new
source ../.aws-creds.sh  # Load AWS credentials
npm start
```

2. **Configure Cline to connect to the running server:**

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://localhost:3001/mcp",
      "transport": "sse"
    }
  }
}
```

**Note:** With SSE transport, you must keep the server running in a terminal. If the server stops, Cline won't be able to use the tools.

---

### 2.3 Verify Cline Connection

After configuring, verify the MCP server is connected:

1. **Restart VS Code** (or reload the window with Cmd+Shift+P → "Reload Window")
2. Open Cline chat panel
3. Look for the MCP server status indicator (should show "lightsail-deployment" as connected)
4. Type: "What MCP tools do you have available?"
5. Cline should list the Lightsail deployment tools including:
   - `analyze_project_intelligently`
   - `generate_smart_deployment_config`
   - `list_lightsail_instances`
   - `diagnose_deployment_issue`
   - And more...

**If tools don't appear:**
- Check the MCP server logs for errors
- Verify the path in your configuration is correct
- Ensure AWS credentials are properly set
- Try restarting VS Code

---

## Step 3: Set Up AWS for GitHub Actions

### 3.1 Create GitHub OIDC Identity Provider

Run this script to set up GitHub OIDC authentication with AWS:

```bash
#!/bin/bash
# setup-github-oidc.sh

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
GITHUB_USERNAME="your-github-username"
REPO_NAME="your-repo-name"

# Create OIDC Provider (only needed once per AWS account)
aws iam create-open-id-connect-provider \
  --url "https://token.actions.githubusercontent.com" \
  --client-id-list "sts.amazonaws.com" \
  --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1" \
  2>/dev/null || echo "OIDC Provider already exists"

# Create IAM Role for GitHub Actions
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${GITHUB_USERNAME}/${REPO_NAME}:*"
        }
      }
    }
  ]
}
EOF

# Create the role
aws iam create-role \
  --role-name "github-actions-${REPO_NAME}" \
  --assume-role-policy-document file://trust-policy.json

# Attach Lightsail policy
aws iam attach-role-policy \
  --role-name "github-actions-${REPO_NAME}" \
  --policy-arn "arn:aws:iam::aws:policy/AmazonLightsailFullAccess"

echo "✅ IAM Role created: arn:aws:iam::${AWS_ACCOUNT_ID}:role/github-actions-${REPO_NAME}"
echo "Add this as AWS_ROLE_ARN variable in your GitHub repository settings"

# Cleanup
rm trust-policy.json
```

### 3.2 Configure GitHub Repository

```bash
# Authenticate with GitHub CLI
gh auth login

# Set the AWS Role ARN as a repository variable
gh variable set AWS_ROLE_ARN \
  --body "arn:aws:iam::YOUR_ACCOUNT_ID:role/github-actions-YOUR_REPO" \
  --repo YOUR_USERNAME/YOUR_REPO
```

---

## Step 4: Deploy Your First Application

### 4.1 Example: Deploy a Node.js Application

Let's deploy a simple Express.js API to Lightsail.

**Step 1: Create Your Application**

```bash
mkdir my-nodejs-app && cd my-nodejs-app

# Create package.json
cat > package.json << 'EOF'
{
  "name": "my-nodejs-app",
  "version": "1.0.0",
  "type": "module",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF

# Create server.js
cat > server.js << 'EOF'
import express from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello from Lightsail!', timestamp: new Date().toISOString() });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
EOF
```

**Step 2: Use Cline to Analyze and Deploy**

Open Cline in VS Code and type:

```
Analyze my Node.js application in the current directory and set up deployment to AWS Lightsail with GitHub Actions.
```

Cline will:
1. Analyze your project using `analyze_project_intelligently`
2. Generate deployment configuration using `generate_smart_deployment_config`
3. Create GitHub Actions workflow
4. Provide instructions for deployment

**Step 3: Review Generated Files**

Cline will create:
- `deployment-nodejs.config.yml` - Deployment configuration
- `.github/workflows/deploy.yml` - GitHub Actions workflow

**Step 4: Push and Deploy**

```bash
# Initialize git and push
git init
git add .
git commit -m "Initial commit with deployment config"
git remote add origin https://github.com/YOUR_USERNAME/my-nodejs-app.git
git push -u origin main
```

The GitHub Actions workflow will automatically deploy your app!

---

## Complete Workflow Examples

### Example 1: Full Deployment with Cline Chat

```
You: Analyze my project and deploy it to Lightsail

Cline: I'll analyze your project and set up deployment. Let me start by examining your codebase...

[Cline calls analyze_project_intelligently]

Based on my analysis:
- Application Type: Node.js (Express)
- Database: None detected
- Recommended Instance: small_3_0 ($10/month)

Would you like me to generate the deployment configuration?

You: Yes, please generate the config and workflow

Cline: [Calls generate_smart_deployment_config]

I've created:
1. deployment-nodejs.config.yml
2. .github/workflows/deploy.yml

To deploy:
1. Push these files to your GitHub repository
2. The workflow will automatically trigger
3. Your app will be available at http://YOUR_INSTANCE_IP

You: Check the deployment status

Cline: [Calls check_deployment_status]

✅ Deployment Status:
- Instance: nodejs-my-app (running)
- IP: 54.123.45.67
- Health: healthy
- Response Time: 45ms

Your application is live at http://54.123.45.67
```

### Example 2: Troubleshooting a Failed Deployment

```
You: My deployment is showing 502 Bad Gateway error

Cline: I'll diagnose the issue. Let me check the instance and logs...

[Calls diagnose_deployment_issue]

🔍 Diagnosis Results:

Root Cause: The Node.js application is not running. PM2 shows the process in "errored" state.

Recommended Actions:
1. Run debug-nodejs.py to get detailed logs
2. Run fix-nodejs.py to restart the application

Would you like me to run the fix script automatically?

You: Yes, fix it

Cline: [Calls run_troubleshooting_script with fix-nodejs.py]

✅ Fix Applied:
- Restarted PM2 processes
- Application is now running
- Health check: passing

Your application should be accessible now.
```

### Example 3: Cost Optimization

```
You: Optimize my infrastructure costs

Cline: [Calls optimize_infrastructure_costs]

💰 Cost Optimization Analysis:

Current Configuration:
- Instance: medium_3_0 ($20/month)
- Database: Local MySQL
- Storage: 20GB

Recommendations:
1. Downsize to small_3_0 - Your traffic doesn't require medium
   Savings: $10/month

2. Enable auto-snapshots instead of continuous backup
   Savings: $2/month

Total Potential Savings: $12/month (37% reduction)

Would you like me to update your configuration?
```

### Example 4: Multi-Service Docker Deployment

```
You: Deploy my Docker Compose application with MySQL and Redis

Cline: [Calls analyze_project_intelligently]

I detected a Docker Compose application with:
- PHP Application (main service)
- MySQL 8.0 (database)
- Redis (caching)

Recommended Configuration:
- Instance: medium_3_0 (Docker needs more resources)
- Bundle: $20/month
- Storage: 40GB SSD

[Calls generate_smart_deployment_config]

Generated files:
1. deployment-docker.config.yml
2. .github/workflows/deploy-docker.yml

The workflow will:
1. Build Docker images
2. Push to instance
3. Run docker-compose up
4. Verify all services are healthy

Push to deploy!
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: MCP Server Not Showing in Cline

**Symptoms:** Cline doesn't show the lightsail-deployment tools

**Solutions:**

1. **Check configuration path:**
```bash
# Verify the server.js path exists
ls -la /full/path/to/lamp-stack-lightsail/mcp-server-new/server.js
```

2. **Test the server manually:**
```bash
cd /path/to/lamp-stack-lightsail/mcp-server-new
source ../.aws-creds.sh
node server.js
```
You should see: `🚀 Enhanced Lightsail Deployment MCP Server v3.0 running on http://0.0.0.0:3001`

3. **Check Cline MCP settings file:**
```bash
# macOS/Linux
cat ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Verify JSON is valid
```

4. **Restart VS Code completely** (not just reload window)

5. **Check for Node.js version:**
```bash
node --version  # Should be 18+
```

#### Issue: MCP Server Crashes on Start

**Check for missing dependencies:**
```bash
cd mcp-server-new
npm install
```

**Check for AWS credential issues:**
```bash
# Verify AWS credentials are set
aws sts get-caller-identity
```

#### Issue: MCP Server Not Connecting

```bash
# Check if server is running
curl http://localhost:3001/health

# If not running, start it
cd mcp-server-new && npm start

# Check for port conflicts
lsof -i :3001
```

#### Issue: AWS Credentials Not Working

```bash
# Verify credentials
aws sts get-caller-identity

# If error, reconfigure
aws configure

# Or source credentials file
source .aws-creds.sh
```

#### Issue: GitHub Actions Failing with OIDC Error

```
Error: Could not assume role with OIDC: Not authorized
```

**Solution:**
1. Verify the IAM role trust policy includes your repository
2. Check the role ARN in GitHub repository variables
3. Ensure OIDC provider is created in AWS

```bash
# Verify role exists
aws iam get-role --role-name github-actions-YOUR_REPO

# Check trust policy
aws iam get-role --role-name github-actions-YOUR_REPO --query 'Role.AssumeRolePolicyDocument'
```

#### Issue: Deployment Health Check Failing

```
You: My deployment shows unhealthy status

Cline: [Calls get_instance_logs]

I found the issue in the logs:
Error: Cannot find module 'express'

The dependencies weren't installed. Let me fix this...

[Calls run_troubleshooting_script]

Fixed! The application is now healthy.
```

### Using Troubleshooting Tools

List available scripts:
```
You: What troubleshooting scripts are available?

Cline: [Calls list_troubleshooting_scripts]

Available scripts by category:

🐳 Docker:
- debug-docker.py - Check Docker container status
- fix-docker.py - Restart Docker containers

📦 Node.js:
- debug-nodejs.py - Check Node.js and PM2 status
- fix-nodejs.py - Fix permissions and restart PM2
- quick-check.py - Quick health check

🌐 Nginx:
- debug-nginx.py - Check Nginx configuration
- fix-nginx.py - Fix Nginx issues

... and more
```

---

## Available MCP Tools Reference

### Core Deployment Tools

| Tool | Description | Example Use |
|------|-------------|-------------|
| `analyze_project_intelligently` | Analyze project to detect type, frameworks, databases | "Analyze my project" |
| `generate_smart_deployment_config` | Generate deployment configuration | "Create deployment config" |
| `setup_intelligent_deployment` | Complete one-click deployment setup | "Set up deployment for my app" |
| `list_lightsail_instances` | List all Lightsail instances | "Show my instances" |
| `check_deployment_status` | Check instance health and status | "Check deployment status" |
| `validate_deployment_config` | Validate configuration file | "Validate my config" |

### AI-Powered Tools

| Tool | Description | Example Use |
|------|-------------|-------------|
| `ai_analyze_project` | Deep AI analysis of project | "AI analyze my code" |
| `ai_troubleshoot` | AI-powered error diagnosis | "Help me fix this error" |
| `ai_ask_expert` | Ask deployment questions | "How do I set up SSL?" |
| `ai_review_config` | AI reviews configuration | "Review my config for issues" |
| `ai_generate_config` | AI generates configuration | "Generate optimal config" |

### Troubleshooting Tools

| Tool | Description | Example Use |
|------|-------------|-------------|
| `list_troubleshooting_scripts` | List available scripts | "What scripts are available?" |
| `run_troubleshooting_script` | Run a specific script | "Run the nodejs fix script" |
| `diagnose_deployment_issue` | AI diagnosis with auto-fix | "Diagnose my 502 error" |
| `get_instance_logs` | Get instance logs | "Show me the application logs" |

### Optimization Tools

| Tool | Description | Example Use |
|------|-------------|-------------|
| `optimize_infrastructure_costs` | Cost optimization analysis | "Optimize my costs" |
| `detect_security_requirements` | Security analysis | "Check security requirements" |

---

## Quick Reference Commands for Cline

### Deployment Commands
- "Analyze and deploy my application"
- "Create deployment config for my Node.js app"
- "Set up GitHub Actions for Lightsail deployment"
- "Deploy my Docker application"

### Status Commands
- "List my Lightsail instances"
- "Check deployment status for my-app"
- "Is my application healthy?"

### Troubleshooting Commands
- "Why is my deployment failing?"
- "Show me the application logs"
- "Fix my 502 Bad Gateway error"
- "Run the nodejs troubleshooting script"

### Optimization Commands
- "Optimize my infrastructure costs"
- "What instance size do I need?"
- "Review my deployment configuration"

---

## Next Steps

1. **Start Simple**: Deploy a basic Node.js or static site first
2. **Add Complexity**: Try Docker or database-backed applications
3. **Automate**: Set up automatic deployments on push
4. **Monitor**: Use the status tools to monitor your deployments
5. **Optimize**: Use cost optimization tools to reduce expenses

---

## Support

- **Issues**: [GitHub Issues](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/issues)
- **Documentation**: [Main README](./README.md)
- **Troubleshooting Tools**: See `troubleshooting-tools/` directory

---

**Happy Deploying! 🚀**
