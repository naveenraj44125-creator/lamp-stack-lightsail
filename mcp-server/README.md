# Lightsail Deployment MCP Server

Model Context Protocol (MCP) server for automated AWS Lightsail deployment with GitHub Actions. This server provides AI assistants with tools to set up, configure, and manage Lightsail deployments.

## Features

- **Setup New Repository**: Create GitHub repos with complete deployment automation
- **Integrate Existing Repos**: Add Lightsail deployment to existing projects
- **Generate Configs**: Create deployment configuration files
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
      "url": "http://your-instance-ip:3000/sse",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

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

Create a new GitHub repository with complete Lightsail deployment automation.

**Parameters:**
- `repo_name` (required): Name of the new repository
- `app_type` (required): Application type (lamp, nginx, nodejs, python, react, docker)
- `instance_name` (required): Lightsail instance name
- `aws_region`: AWS region (default: us-east-1)
- `enable_bucket`: Enable S3 bucket integration (default: false)
- `bucket_name`: S3 bucket name (if enable_bucket is true)
- `database_type`: Database type (none, mysql, postgresql)
- `use_rds`: Use AWS RDS for database (default: false)

**Example:**
```
Create a new repository called "my-app" with Node.js deployment to Lightsail instance "my-nodejs-app" in us-west-2
```

### 2. integrate_existing_repository

Add Lightsail deployment automation to an existing GitHub repository.

**Parameters:**
- `repo_path` (required): Path to existing repository
- `app_type` (required): Application type
- `instance_name` (required): Lightsail instance name
- `aws_region`: AWS region (default: us-east-1)
- `enable_bucket`: Enable S3 bucket (default: false)

**Example:**
```
Add Lightsail deployment to my existing repo at /path/to/repo for a LAMP stack app
```

### 3. generate_deployment_config

Generate a deployment configuration file for Lightsail.

**Parameters:**
- `app_type` (required): Application type
- `instance_name` (required): Instance name
- `dependencies`: Additional dependencies (redis, git, etc.)
- `enable_bucket`: Enable S3 bucket (default: false)
- `bucket_config`: Bucket configuration object

**Example:**
```
Generate a deployment config for a Python app with Redis
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
