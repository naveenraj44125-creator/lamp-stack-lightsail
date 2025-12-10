# Lightsail Deployment MCP Server

Model Context Protocol (MCP) server for automated AWS Lightsail deployment with GitHub Actions. This server provides AI assistants with tools to set up, configure, and manage Lightsail deployments.

## Features

- **Setup New Repository**: Create GitHub repos with complete deployment automation
- **Integrate Existing Repos**: Add Lightsail deployment to existing projects
- **Multi-OS Support**: Deploy to Ubuntu, Amazon Linux, or CentOS instances
- **Flexible Instance Sizes**: Choose from Nano (512MB) to 2XLarge (32GB) instances
- **Generate Configs**: Create deployment configuration files with OS-specific settings
- **OIDC Setup**: Configure GitHub Actions authentication with AWS
- **Deployment Status**: Monitor workflow runs and deployment health
- **Example Apps**: List available application templates
- **Diagnostics**: Troubleshoot deployment issues with automated checks

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

**7 tools available for complete deployment automation and troubleshooting:**

### 1. setup_new_repository

Create a new GitHub repository with complete Lightsail deployment automation. **Now supports multiple operating systems and instance sizes!**

**Parameters:**
- `repo_name` (required): Name of the new repository
- `app_type` (required): Application type (lamp, nginx, nodejs, python, react, docker)
- `instance_name` (required): Lightsail instance name
- `aws_region`: AWS region (default: us-east-1)
- `blueprint_id`: Operating system blueprint (default: ubuntu_22_04)
  - `ubuntu_22_04`: Ubuntu 22.04 LTS (Recommended)
  - `ubuntu_20_04`: Ubuntu 20.04 LTS
  - `amazon_linux_2023`: Amazon Linux 2023
  - `amazon_linux_2`: Amazon Linux 2
  - `centos_7_2009_01`: CentOS 7
- `bundle_id`: Instance size bundle (default: small_3_0)
  - `nano_3_0`: Nano (512MB RAM, $3.50/month)
  - `micro_3_0`: Micro (1GB RAM, $5/month)
  - `small_3_0`: Small (2GB RAM, $10/month) - Recommended
  - `medium_3_0`: Medium (4GB RAM, $20/month)
  - `large_3_0`: Large (8GB RAM, $40/month)
  - `xlarge_3_0`: XLarge (16GB RAM, $80/month)
  - `2xlarge_3_0`: 2XLarge (32GB RAM, $160/month)
- `enable_bucket`: Enable S3 bucket integration (default: false)
- `bucket_name`: S3 bucket name (if enable_bucket is true)
- `database_type`: Database type (none, mysql, postgresql)
- `use_rds`: Use AWS RDS for database (default: false)

**Examples:**
```
Create a new repository called "my-app" with Node.js deployment to Lightsail instance "my-nodejs-app" in us-west-2
```

```
Create a new Python app on Amazon Linux 2023 with a Medium instance size
```

```
Set up a LAMP stack on Ubuntu 22.04 with XLarge instance for high traffic
```

### 2. integrate_existing_repository

Add Lightsail deployment automation to an existing GitHub repository. **Supports multiple operating systems and instance sizes!**

**Parameters:**
- `repo_path` (required): Path to existing repository
- `app_type` (required): Application type
- `instance_name` (required): Lightsail instance name
- `aws_region`: AWS region (default: us-east-1)
- `blueprint_id`: Operating system blueprint (default: ubuntu_22_04)
- `bundle_id`: Instance size bundle (default: small_3_0)
- `enable_bucket`: Enable S3 bucket (default: false)

**Examples:**
```
Add Lightsail deployment to my existing repo at /path/to/repo for a LAMP stack app
```

```
Integrate Lightsail deployment with Amazon Linux 2023 and Small instance size
```

### 3. generate_deployment_config

Generate a deployment configuration file for Lightsail with OS and instance size selection.

**Parameters:**
- `app_type` (required): Application type
- `instance_name` (required): Instance name
- `blueprint_id`: Operating system blueprint (default: ubuntu_22_04)
- `bundle_id`: Instance size bundle (default: small_3_0)
- `dependencies`: Additional dependencies (redis, git, etc.)
- `enable_bucket`: Enable S3 bucket (default: false)
- `bucket_config`: Bucket configuration object

**Examples:**
```
Generate a deployment config for a Python app with Redis
```

```
Create a config for Docker deployment on Amazon Linux 2023 with Large instance
```

### 4. setup_oidc_authentication

Set up GitHub Actions OIDC authentication with AWS.

**Parameters:**
- `repo_owner` (required): GitHub repository owner
- `repo_name` (required): GitHub repository name
- `role_name` (required): IAM role name to create
- `trust_branch`: Branch to trust for deployments (default: main)

**Example:**
```
Set up OIDC for my-org/my-repo with role name "github-actions-lightsail"
```

### 5. get_deployment_status

Check the status of Lightsail deployments.

**Parameters:**
- `repo_path` (required): Path to repository

**Example:**
```
Check deployment status for my repository
```

### 6. list_available_examples

List all available example applications and their features.

**Example:**
```
What example applications are available?
```

### 7. diagnose_deployment

Run diagnostics to troubleshoot deployment issues. Checks prerequisites, configuration, and common problems.

**Parameters:**
- `repo_path`: Path to repository (optional, defaults to current directory)
- `check_type`: Type of diagnostic check (all, prerequisites, configuration, github, aws, instance)

**Example:**
```
Diagnose my deployment setup
```

or

```
Check my AWS configuration for deployment issues
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
