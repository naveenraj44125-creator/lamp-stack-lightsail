# Lightsail Deployment MCP Server

Model Context Protocol (MCP) server for automated AWS Lightsail deployment with GitHub Actions. This server provides AI assistants with tools to set up, configure, and manage comprehensive Lightsail deployments with enhanced automation capabilities.

## Features

- **Complete Deployment Setup**: Enhanced setup script for comprehensive deployment automation
- **6 Application Types**: LAMP, Node.js, Python, React, Docker, and Nginx applications
- **Universal Database Support**: MySQL, PostgreSQL, or none - available for ALL application types
- **GitHub OIDC Integration**: Secure AWS authentication without storing credentials
- **Lightsail Bucket Storage**: Optional S3-compatible storage integration
- **Multi-OS Support**: Deploy to Ubuntu, Amazon Linux, or CentOS instances
- **Flexible Instance Sizes**: Choose from Nano (512MB) to 2XLarge (8GB) instances
- **Client-Side Execution**: All operations run on your local machine, not the MCP server
- **Deployment Examples**: Ready-to-use configurations and workflows
- **Comprehensive Diagnostics**: Troubleshoot deployment issues with automated checks

## Installation

### Option 1: Remote Server (Recommended for Teams)

Deploy on your Lightsail instance for remote access:

```bash
./deploy-to-lightsail.sh your-instance-ip
```

Then configure clients:
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://18.215.231.164:3000/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

**Current Live Server:** `http://18.215.231.164:3000`
- Health Check: `http://18.215.231.164:3000/health`
- Web Interface: `http://18.215.231.164:3000/`
- SSE Endpoint: `http://18.215.231.164:3000/sse`

See [DEPLOY.md](DEPLOY.md) for complete deployment guide.

### Option 2: NPX (Zero Install)

No installation needed! Just configure your MCP client:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "npx",
      "args": ["-y", "lightsail-deployment-mcp"]
    }
  }
}
```

### Option 3: Global NPM Install

```bash
npm install -g lightsail-deployment-mcp
```

Then configure:
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "lightsail-deployment-mcp"
    }
  }
}
```

### Option 4: Local Development

```bash
cd mcp-server
npm install
npm link
```

## Configuration

Add to your MCP client configuration (e.g., Claude Desktop, Kiro):

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "lightsail-deployment-mcp"
    }
  }
}
```

For local development:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "node",
      "args": ["/path/to/mcp-server/index.js"]
    }
  }
}
```

## Available Tools

**4 tools available for complete deployment automation and troubleshooting:**

### 1. setup_complete_deployment

Get the enhanced setup script for creating complete Lightsail deployment automation. **This tool provides instructions to run the setup script on your local machine, not on the MCP server.**

**Features:**
- **6 Application Types**: LAMP, Node.js, Python, React, Docker, Nginx
- **Universal Database Support**: MySQL, PostgreSQL, or none (available for ALL app types)
- **GitHub OIDC Integration**: Secure AWS authentication without storing credentials
- **Lightsail Bucket Storage**: Optional S3-compatible storage integration
- **Multi-OS Support**: Ubuntu, Amazon Linux, CentOS
- **Instance Sizing**: Nano (512MB) to 2XLarge (8GB RAM)

**Parameters:**
- `mode`: Script execution mode (interactive, auto, help) - default: interactive
- `aws_region`: AWS region for deployment - default: us-east-1
- `app_version`: Application version - default: 1.0.0

**Examples:**
```
Get the setup script for interactive deployment configuration
```

```
Get setup instructions for automatic mode in us-west-2 region
```

```
Show help and usage information for the setup script
```

### 2. get_deployment_examples

Get example deployment configurations and GitHub Actions workflows for different application types. Returns ready-to-use configuration files and deployment examples.

**Parameters:**
- `app_type`: Application type (lamp, nginx, nodejs, python, react, docker, all) - default: all
- `include_configs`: Include deployment configuration files - default: true
- `include_workflows`: Include GitHub Actions workflow examples - default: true

**Examples:**
```
Get all deployment examples and configurations
```

```
Get only Node.js deployment examples with workflows
```

```
Show me LAMP stack configuration files
```

### 3. get_deployment_status

Check deployment status and GitHub Actions workflow runs. Monitor active deployments and view recent workflow execution results.

**Parameters:**
- `repo_path` (required): Repository path to check

**Example:**
```
Check deployment status for my repository at /path/to/repo
```

### 4. diagnose_deployment

Run comprehensive deployment diagnostics and troubleshooting. Check prerequisites, repository status, configuration files, and provide next steps.

**Parameters:**
- `repo_path`: Path to repository (optional, defaults to current directory)
- `check_type`: Type of diagnostic check (all, prerequisites, configuration, github, aws, instance) - default: all

**Examples:**
```
Diagnose my deployment setup and check all prerequisites
```

```
Check only AWS configuration for deployment issues
```

```
Run full diagnostics on my repository at /path/to/repo
```

## Usage Examples

### Setting Up a New Project

```
AI: I'll help you set up a new Lightsail deployment.

User: Create a new Node.js app called "my-api" deployed to instance "api-prod"

AI: [Uses setup_new_repository tool]
✅ Repository setup prepared!
Next steps:
1. Create GitHub repository: gh repo create my-api --public
2. Copy files from: /tmp/lightsail-1234567890
3. Push to GitHub
4. Set up OIDC authentication
```

### Adding to Existing Project

```
User: Add Lightsail deployment to my existing React app at ./my-react-app

AI: [Uses integrate_existing_repository tool]
✅ Lightsail deployment integrated!
Added workflows, deployment scripts, and configuration.
Commit and push to trigger deployment.
```

### Checking Deployment Status

```
User: What's the status of my deployments?

AI: [Uses get_deployment_status tool]
# Deployment Status

✅ **Deploy to Lightsail** - completed
   https://github.com/user/repo/actions/runs/123456

🔄 **Deploy to Lightsail** - in_progress
   https://github.com/user/repo/actions/runs/123457
```

## Requirements

- Node.js 18+
- GitHub CLI (`gh`) installed and authenticated
- AWS CLI configured (for OIDC setup)
- Git

## Supported Application Types

- **LAMP**: Apache + PHP + MySQL/PostgreSQL
- **NGINX**: Static file serving, reverse proxy
- **Node.js**: Express, Next.js, NestJS, APIs
- **Python**: Flask, Django, FastAPI
- **React**: CRA, Vite, Next.js static
- **Docker**: Multi-container, microservices

## Operating System Support

The MCP server now supports multiple operating systems with automatic package manager detection:

- **Ubuntu 22.04 LTS** (Recommended) - `ubuntu_22_04`
- **Ubuntu 20.04 LTS** - `ubuntu_20_04`
- **Amazon Linux 2023** - `amazon_linux_2023`
- **Amazon Linux 2** - `amazon_linux_2`
- **CentOS 7** - `centos_7_2009_01`

Each OS is automatically configured with the appropriate package manager (apt for Ubuntu, yum/dnf for Amazon Linux/CentOS) and system-specific settings.

## Instance Size Options

Choose the right instance size for your workload:

| Size | RAM | vCPU | Storage | Monthly Cost | Best For |
|------|-----|------|---------|--------------|----------|
| Nano | 512MB | 1 | 20GB SSD | $3.50 | Lightest workloads |
| Micro | 1GB | 1 | 40GB SSD | $5.00 | Small apps |
| Small | 2GB | 2 | 60GB SSD | $10.00 | Most apps (Recommended) |
| Medium | 4GB | 2 | 80GB SSD | $20.00 | High traffic apps |
| Large | 8GB | 4 | 160GB SSD | $40.00 | Resource intensive |
| XLarge | 16GB | 4 | 320GB SSD | $80.00 | Heavy workloads |
| 2XLarge | 32GB | 8 | 640GB SSD | $160.00 | Enterprise |

## Development

```bash
# Install dependencies
npm install

# Run locally
npm start

# Test with MCP inspector
npx @modelcontextprotocol/inspector node index.js
```

## License

MIT

## Support

For issues and questions, visit: https://github.com/naveenraj44125-creator/lamp-stack-lightsail
