# 🚀 Enhanced Lightsail Deployment MCP Server v3.0.0

An intelligent Model Context Protocol (MCP) server that provides **fully automated AWS Lightsail deployment** with smart project analysis, cost optimization, security assessment, and **AI-powered assistance via AWS Bedrock**.

## 🎯 One-Command Deployment

Deploy any application with a single API call - **zero manual steps**:

```bash
# Start the server
npm start

# Deploy your app (in another terminal)
curl -X POST http://localhost:3001/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "setup_intelligent_deployment",
    "arguments": {
      "project_path": "/path/to/your/app",
      "app_name": "my-app",
      "github_config": {
        "username": "your-github-username",
        "repository": "my-app"
      }
    }
  }'
```

**What happens automatically:**
- ✅ Project analysis (detects Node.js, Python, PHP, React, Docker)
- ✅ Git initialization (if needed)
- ✅ GitHub repository creation
- ✅ IAM role setup for GitHub OIDC
- ✅ GitHub secrets configuration
- ✅ Deployment config & workflow generation
- ✅ Push to trigger GitHub Actions
- ✅ Lightsail instance creation & app deployment

**Smart Detection:**
- Auto-detects application port from your code (`process.env.PORT || 3000`)
- Recognizes frameworks (Express, Flask, Laravel, React, Vue, etc.)
- Configures appropriate instance size based on app requirements
- Sets up health checks automatically

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [AWS Credentials Configuration](#-aws-credentials-configuration)
- [Transport Modes](#-transport-modes)
- [Available Tools (18 Total)](#-available-tools)
- [Cline/MCP Client Integration](#-clinemcp-client-integration)
- [Troubleshooting Tools](#-troubleshooting-tools-directory)
- [AWS Bedrock AI Integration](#-aws-bedrock-ai-integration)
- [Tool Usage Examples](#-tool-usage-examples)
- [Configuration Reference](#-configuration-reference)
- [Testing](#-testing)
- [Support](#-support)

---

## ✨ Features

### 🤖 AI-Powered Analysis (AWS Bedrock)
- **Intelligent Code Analysis**: Uses Claude via Bedrock to understand your codebase
- **Smart Troubleshooting**: AI-powered error diagnosis and solutions
- **Expert Q&A**: Ask deployment questions and get expert answers
- **Config Review**: AI reviews your configs for security and optimization
- **Code Explanation**: Understand code from a deployment perspective

### 🔍 Intelligent Project Analysis
- **Automatic Application Type Detection**: Node.js, Python, PHP, React, Docker, or static
- **Framework Recognition**: Express, Flask, Laravel, React, Vue, Angular, and more
- **Database Requirements**: MySQL, PostgreSQL, MongoDB detection
- **Storage Needs**: File upload requirements and S3 bucket needs
- **Security Analysis**: Authentication, user data handling, security requirements

### 💰 Cost Optimization
- **Right-Sizing**: Optimal instance sizes based on application requirements
- **Database Optimization**: Local vs RDS database configurations
- **Storage Optimization**: S3 bucket configurations
- **Cost Estimation**: Accurate monthly cost estimates

### 🔒 Security Assessment
- **Compliance Support**: GDPR, HIPAA, SOC2, PCI-DSS configurations
- **SSL/TLS Configuration**: Automatic HTTPS setup
- **Firewall Rules**: Intelligent firewall configuration
- **Data Protection**: Encryption recommendations

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MCP Server (server.js - 3217 lines)                  │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  Transport      │  │  Tool Handlers  │  │  AWS Integration        │ │
│  │  ─────────────  │  │  ─────────────  │  │  ─────────────────────  │ │
│  │  • stdio        │  │  • 8 Core Tools │  │  • Lightsail SDK        │ │
│  │  • HTTP/SSE     │  │  • 6 AI Tools   │  │  • Bedrock Runtime      │ │
│  │                 │  │  • 4 Debug Tools│  │  • Credential Provider  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘ │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Supporting Modules                            │   │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │   │
│  │  │ project-analyzer │ │ infrastructure-  │ │ configuration-   │ │   │
│  │  │ .js              │ │ optimizer.js     │ │ generator.js     │ │   │
│  │  │ ────────────────│ │ ────────────────│ │ ────────────────│ │   │
│  │  │ • Type detection │ │ • Cost analysis  │ │ • YAML configs   │ │   │
│  │  │ • Framework scan │ │ • Right-sizing   │ │ • GitHub Actions │ │   │
│  │  │ • DB detection   │ │ • Performance    │ │ • Env variables  │ │   │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │ bedrock-ai.js                                             │   │   │
│  │  │ ────────────────────────────────────────────────────────  │   │   │
│  │  │ • Claude 3 Sonnet (default) / Haiku (quick tasks)         │   │   │
│  │  │ • 3 credential methods: Profile, Direct, Default Chain    │   │   │
│  │  │ • AI analysis, troubleshooting, config generation         │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  External: ../troubleshooting-tools/ (7 categories, 40+ scripts)│   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/naveenraj44125-creator/lamp-stack-lightsail.git
cd lamp-stack-lightsail/mcp-server-new

# Install dependencies
npm install
```

### Running the Server

```bash
# Stdio mode (for Cline/MCP clients)
node server.js --stdio

# HTTP/SSE mode (for web clients)
npm start
# Or with custom port
PORT=3002 npm start
```

---

## 🔐 AWS Credentials Configuration

The MCP server supports **three methods** for AWS credential configuration, in order of precedence:

### Method 1: AWS Profile (Recommended) ⭐

The cleanest and most secure approach - uses profiles from `~/.aws/credentials`:

```bash
# In your ~/.aws/credentials file:
[my-lightsail-profile]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = us-east-1
```

**For Cline/MCP Client:**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-server-new/server.js", "--stdio"],
      "env": {
        "AWS_PROFILE": "my-lightsail-profile",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

**For Terminal:**
```bash
export AWS_PROFILE=my-lightsail-profile
node server.js --stdio
```

### Method 2: Environment Variables

Direct credentials via environment variables:

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_REGION=us-east-1
node server.js --stdio
```

**For Cline/MCP Client:**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-server-new/server.js", "--stdio"],
      "env": {
        "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
        "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

### Method 3: Per-Request Credentials

Pass credentials directly in tool calls (useful for multi-account scenarios):

```javascript
{
  "name": "ai_troubleshoot",
  "arguments": {
    "error_message": "Connection refused",
    "aws_credentials": {
      "profile": "my-profile"  // Use profile
      // OR direct credentials:
      // "access_key_id": "AKIA...",
      // "secret_access_key": "...",
      // "session_token": "...",  // Optional, for temporary creds
      // "region": "us-east-1"
    }
  }
}
```

### Credential Resolution Order

```
1. Per-request credentials (aws_credentials in tool input)
   ↓ (if not provided)
2. AWS_PROFILE environment variable → reads ~/.aws/credentials
   ↓ (if not set)
3. AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY environment variables
   ↓ (if not set)
4. Default AWS credential chain (IAM role, instance profile, etc.)
```

---

## 🔄 Transport Modes

### Stdio Mode (for MCP Clients)

Used by Cline, Claude Desktop, and other MCP-compatible clients:

```bash
node server.js --stdio
```

Communication happens via stdin/stdout using JSON-RPC.

### HTTP/SSE Mode (for Web Clients)

Starts an HTTP server with Server-Sent Events for real-time updates:

```bash
npm start
# Server starts on http://localhost:3001

# Endpoints:
# GET  /health      - Health check
# GET  /tools       - List all available tools
# POST /call-tool   - Execute a tool directly
# POST /mcp         - MCP protocol endpoint
# GET  /sse         - Server-Sent Events stream
```

#### Direct Tool Execution via HTTP

```bash
# List available tools
curl http://localhost:3001/tools

# Execute a tool
curl -X POST http://localhost:3001/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "list_lightsail_instances",
    "arguments": {
      "aws_region": "us-east-1"
    }
  }'

# Full deployment
curl -X POST http://localhost:3001/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "setup_intelligent_deployment",
    "arguments": {
      "project_path": "/path/to/app",
      "app_name": "my-app",
      "github_config": {
        "username": "github-user",
        "repository": "my-app"
      }
    }
  }'
```

---

## 🛠️ Available Tools

The MCP server provides **18 tools** across three categories:

### Core Tools (8)

| Tool | Description |
|------|-------------|
| `analyze_project_intelligently` | Analyze project to detect app type, frameworks, databases |
| `generate_smart_deployment_config` | Generate optimized deployment configuration |
| `setup_intelligent_deployment` | One-click deployment setup (analysis + config + GitHub Actions) |
| `optimize_infrastructure_costs` | Analyze and optimize infrastructure costs |
| `detect_security_requirements` | Analyze security requirements and generate configs |
| `list_lightsail_instances` | List all Lightsail instances in a region |
| `check_deployment_status` | Check deployment health and status |
| `validate_deployment_config` | Validate deployment configuration |

### AI-Powered Tools (6) - Requires AWS Bedrock

| Tool | Description |
|------|-------------|
| `ai_analyze_project` | Claude AI analyzes project files intelligently |
| `ai_troubleshoot` | AI-powered error diagnosis and solutions |
| `ai_ask_expert` | Ask the AI deployment expert any question |
| `ai_review_config` | AI reviews config for security and optimization |
| `ai_explain_code` | AI explains code from deployment perspective |
| `ai_generate_config` | AI generates complete deployment configuration |

### Troubleshooting Tools (4)

| Tool | Description |
|------|-------------|
| `list_troubleshooting_scripts` | List available troubleshooting scripts by category |
| `run_troubleshooting_script` | Run a specific troubleshooting script on an instance |
| `diagnose_deployment_issue` | AI-powered diagnosis with script recommendations |
| `get_instance_logs` | Retrieve logs from a Lightsail instance |

---

## 🔗 Cline/MCP Client Integration

### Complete Cline Configuration

Add to your Cline MCP settings (`~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`):

**Using AWS Profile (Recommended):**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "node",
      "args": ["/Users/yourname/projects/lamp-stack-lightsail/mcp-server-new/server.js", "--stdio"],
      "env": {
        "AWS_PROFILE": "your-aws-profile",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

**Using Direct Credentials:**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "node",
      "args": ["/Users/yourname/projects/lamp-stack-lightsail/mcp-server-new/server.js", "--stdio"],
      "env": {
        "AWS_ACCESS_KEY_ID": "your-access-key",
        "AWS_SECRET_ACCESS_KEY": "your-secret-key",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

### Verify Integration

After configuring, ask Cline:
- "List my Lightsail instances"
- "Analyze this project for deployment"
- "What troubleshooting scripts are available?"

### 💬 Sample Prompts for Each Tool

Use these natural language prompts in Cline to invoke each MCP tool:

#### Core Tools (8)

| Tool | Sample Prompts |
|------|----------------|
| `analyze_project_intelligently` | "Analyze my project at /path/to/app for deployment"<br>"What type of application is this and what does it need to deploy?"<br>"Scan this Node.js project and tell me the dependencies and database requirements" |
| `generate_smart_deployment_config` | "Generate a deployment config for my-app based on the analysis"<br>"Create a deployment.config.yml for this Express app"<br>"Generate optimized Lightsail config for production deployment" |
| `setup_intelligent_deployment` | "Deploy my app at /path/to/app to Lightsail with GitHub Actions"<br>"Set up complete deployment for my-api with GitHub username naveenraj44125-creator"<br>"One-click deploy this project to AWS Lightsail" |
| `optimize_infrastructure_costs` | "Optimize the infrastructure costs for my deployment"<br>"What's the cheapest Lightsail setup for my small Node.js API?"<br>"Analyze my config and suggest cost savings" |
| `detect_security_requirements` | "What security settings does my app need?"<br>"Analyze security requirements for this project with GDPR compliance"<br>"Generate firewall rules and SSL config for my deployment" |
| `list_lightsail_instances` | "List all my Lightsail instances"<br>"Show me running instances in us-west-2"<br>"What Lightsail servers do I have?" |
| `check_deployment_status` | "Check if my-app is healthy"<br>"What's the status of nodejs-demo-app instance?"<br>"Is my deployment at /api/health responding?" |
| `validate_deployment_config` | "Validate my deployment config file"<br>"Check if deployment-nodejs.config.yml is correct"<br>"Are there any issues with my deployment configuration?" |

#### AI-Powered Tools (6)

| Tool | Sample Prompts |
|------|----------------|
| `ai_analyze_project` | "Use AI to analyze my project files for deployment"<br>"Have Claude look at my codebase and recommend deployment settings"<br>"AI analysis of this Flask app - what infrastructure does it need?" |
| `ai_troubleshoot` | "AI help: my app shows ECONNREFUSED 127.0.0.1:27017"<br>"Troubleshoot this error: 502 Bad Gateway on my Node.js app"<br>"Why is my deployment failing with this error log?" |
| `ai_ask_expert` | "How do I set up SSL for my Lightsail instance?"<br>"What's the best way to handle environment variables in deployment?"<br>"Expert advice: should I use RDS or local database for my small app?" |
| `ai_review_config` | "Review my deployment config for security issues"<br>"AI check this config for optimization opportunities"<br>"Is my deployment.config.yml following best practices?" |
| `ai_explain_code` | "Explain this server.js from a deployment perspective"<br>"What ports and env vars does this code need?"<br>"AI explain what infrastructure this code requires" |
| `ai_generate_config` | "AI generate a complete deployment config for my analyzed project"<br>"Create production-ready config based on this analysis"<br>"Generate optimal Lightsail configuration using AI" |

#### Troubleshooting Tools (4)

| Tool | Sample Prompts |
|------|----------------|
| `list_troubleshooting_scripts` | "What troubleshooting scripts are available?"<br>"Show me Node.js debugging scripts"<br>"List all nginx troubleshooting tools" |
| `run_troubleshooting_script` | "Run debug-nodejs.py on my-app instance"<br>"Execute the nginx fix script on web-server"<br>"Run fix-lamp.py to repair my PHP deployment" |
| `diagnose_deployment_issue` | "Diagnose why my-app is returning 502 errors"<br>"Figure out what's wrong with my Node.js deployment"<br>"Auto-diagnose and fix the deployment issue on my-api" |
| `get_instance_logs` | "Get logs from my-app instance"<br>"Show me the last 100 lines of nginx logs"<br>"Fetch PM2 logs from nodejs-server" |

#### Complete Workflow Prompts

**Full Deployment (Recommended):**
```
Deploy my Node.js app at ./my-project to Lightsail. 
My GitHub username is myuser and I want the repo called my-app.
Use production settings with standard budget.
```

**Troubleshooting Workflow:**
```
My app my-api is showing 502 Bad Gateway errors.
It's a Node.js Express app. Please diagnose the issue 
and automatically fix it if possible.
```

**Cost Optimization:**
```
Analyze my current deployment config and suggest ways 
to reduce costs while maintaining good performance 
for a low-traffic API.
```

**Security Review:**
```
Review my deployment for security issues. 
The app handles user data and needs GDPR compliance.
Generate appropriate security configurations.
```

For detailed integration guide, see: **[CLINE-INTEGRATION-GUIDE.md](./CLINE-INTEGRATION-GUIDE.md)**

---

## 📁 Troubleshooting Tools Directory

The server integrates with `../troubleshooting-tools/` containing **40+ scripts** across 7 categories:

```
troubleshooting-tools/
├── docker/                          # Docker/container issues
│   ├── debug-docker.py              # Diagnose Docker problems
│   ├── fix-docker.py                # Auto-fix Docker issues
│   └── README.md
│
├── general/                         # Cross-platform tools
│   ├── comprehensive-endpoint-check.py
│   ├── extract-instance-info.py
│   ├── final-deployment-verification.py
│   ├── fix-all-deployment-issues.py
│   ├── monitor-deployment-progress.py
│   ├── quick-endpoint-check.py
│   ├── test-all-deployments.py
│   ├── verify-all-8-deployments.py
│   ├── verify-all-endpoints.py
│   └── verify-new-deployments-v7.py
│
├── lamp/                            # LAMP stack (Linux/Apache/MySQL/PHP)
│   ├── debug-lamp.py
│   ├── diagnose-lamp-failure.py
│   ├── fix-lamp-amazon-linux-remote.py
│   ├── fix-lamp-amazon-linux.py
│   ├── fix-lamp.py
│   └── README.md
│
├── nginx/                           # Nginx web server
│   ├── check_nginx_config.py
│   ├── debug-nginx.py
│   ├── fix-nginx-default-page.py
│   ├── fix-nginx-verification.py
│   ├── fix-nginx.py
│   └── README.md
│
├── nodejs/                          # Node.js applications
│   ├── debug-instagram-clone.py
│   ├── debug-nodejs.py
│   ├── debug-react-nodejs.py
│   ├── fix-instagram-clone.py
│   ├── fix-nodejs.py
│   ├── fix-react-nodejs.py
│   ├── manual-test.py
│   ├── quick-check.py
│   └── README.md
│
├── python/                          # Python/Flask applications
│   ├── debug-python.py
│   ├── final-python-fix.py
│   ├── fix-python.py
│   └── README.md
│
├── react/                           # React/frontend applications
│   ├── debug-react.py
│   ├── fix-react.py
│   └── README.md
│
├── debug-mongodb-test.sh            # MongoDB debugging
└── fix-reddit-mysql.py              # MySQL fixes
```

### Using Troubleshooting Tools via MCP

```javascript
// List all available scripts
{ "name": "list_troubleshooting_scripts", "arguments": { "category": "all" } }

// List scripts for specific category
{ "name": "list_troubleshooting_scripts", "arguments": { "category": "nodejs" } }

// Run a debug script
{
  "name": "run_troubleshooting_script",
  "arguments": {
    "script_name": "debug-nodejs.py",
    "category": "nodejs",
    "instance_name": "my-nodejs-app",
    "aws_region": "us-east-1"
  }
}

// AI-powered diagnosis with auto-fix
{
  "name": "diagnose_deployment_issue",
  "arguments": {
    "instance_name": "my-app",
    "error_description": "502 Bad Gateway",
    "app_type": "nodejs",
    "auto_fix": true
  }
}
```

---

## 🤖 AWS Bedrock AI Integration

### Supported Models

| Model | ID | Use Case |
|-------|-----|----------|
| **Claude 3 Sonnet** | `anthropic.claude-3-sonnet-20240229-v1:0` | Default - balanced performance |
| **Claude 3 Haiku** | `anthropic.claude-3-haiku-20240307-v1:0` | Quick tasks, lower cost |
| **Claude 3 Opus** | `anthropic.claude-3-opus-20240229-v1:0` | Complex analysis |

### Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.*"
    }
  ]
}
```

### Enable Bedrock Models

1. Go to AWS Console → Amazon Bedrock
2. Navigate to "Model access"
3. Request access to Claude models
4. Wait for approval (usually instant for Claude)

### Test Bedrock Connection

```bash
# Set credentials
export AWS_PROFILE=your-profile

# Run test
node test-bedrock-ai.js
```

---

## 📖 Tool Usage Examples

### Analyze and Deploy a Project

```javascript
// Step 1: Analyze project
{
  "name": "analyze_project_intelligently",
  "arguments": {
    "project_path": "/path/to/your/project",
    "user_description": "A Node.js API with PostgreSQL"
  }
}

// Step 2: Generate deployment config
{
  "name": "generate_smart_deployment_config",
  "arguments": {
    "analysis_result": { /* from step 1 */ },
    "app_name": "my-api",
    "aws_region": "us-east-1"
  }
}

// Or use one-click setup
{
  "name": "setup_intelligent_deployment",
  "arguments": {
    "project_path": "/path/to/project",
    "app_name": "my-api",
    "deployment_preferences": {
      "budget": "standard",
      "scale": "small",
      "environment": "production"
    }
  }
}
```

### Troubleshooting Workflow

```javascript
// Step 1: Check status
{
  "name": "check_deployment_status",
  "arguments": {
    "instance_name": "my-app",
    "health_check_endpoint": "/api/health"
  }
}

// Step 2: Get logs if unhealthy
{
  "name": "get_instance_logs",
  "arguments": {
    "instance_name": "my-app",
    "log_type": "all",
    "lines": 200
  }
}

// Step 3: AI diagnosis
{
  "name": "diagnose_deployment_issue",
  "arguments": {
    "instance_name": "my-app",
    "error_description": "502 Bad Gateway",
    "app_type": "nodejs",
    "auto_fix": true
  }
}
```

### AI-Powered Assistance

```javascript
// Ask the expert
{
  "name": "ai_ask_expert",
  "arguments": {
    "question": "How do I set up SSL for my Node.js app on Lightsail?",
    "project_context": { "app_type": "nodejs", "has_domain": true }
  }
}

// Review configuration
{
  "name": "ai_review_config",
  "arguments": {
    "config": { /* your deployment config */ }
  }
}

// Troubleshoot error
{
  "name": "ai_troubleshoot",
  "arguments": {
    "error_message": "ECONNREFUSED 127.0.0.1:27017",
    "context": { "app_type": "nodejs", "database": "mongodb" }
  }
}
```

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_PROFILE` | - | AWS profile name from ~/.aws/credentials |
| `AWS_REGION` | `us-east-1` | Default AWS region |
| `AWS_ACCESS_KEY_ID` | - | AWS access key (if not using profile) |
| `AWS_SECRET_ACCESS_KEY` | - | AWS secret key (if not using profile) |
| `PORT` | `3001` | HTTP server port |
| `HOST` | `0.0.0.0` | HTTP server host |
| `MCP_AUTH_TOKEN` | - | Optional authentication token |
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-sonnet-20240229-v1:0` | Bedrock model |

### Deployment Preferences

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `budget` | `minimal`, `standard`, `performance` | `standard` | Budget tier |
| `scale` | `small`, `medium`, `large` | `small` | Scale tier |
| `environment` | `development`, `staging`, `production` | `production` | Environment |
| `api_only_app` | `true`, `false` | `false` | For API-only apps |
| `verification_endpoint` | string | `/` | Custom verification endpoint |
| `health_check_endpoint` | string | `/` | Custom health check endpoint |

---

## 🧪 Testing

```bash
# Unit tests
npm test

# Test specific components
node test-new-tools.js        # New tools and validation
node test-components.js       # MCP components
node test-bedrock-ai.js       # Bedrock AI integration

# E2E deployment test
node test-e2e-deployment.js --dry-run    # Dry run
node test-e2e-deployment.js              # Full test
node test-e2e-deployment.js --cleanup    # Cleanup resources
```

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/issues)
- **Discussions**: [GitHub Discussions](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/discussions)
- **Integration Guide**: [CLINE-INTEGRATION-GUIDE.md](./CLINE-INTEGRATION-GUIDE.md)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

**Made with ❤️ for developers who want intelligent infrastructure automation**
