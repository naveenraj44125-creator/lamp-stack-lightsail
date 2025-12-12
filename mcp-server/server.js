#!/usr/bin/env node

/**
 * HTTP/SSE Server for Lightsail Deployment MCP
 * 
 * This server exposes the MCP server over HTTP using Server-Sent Events (SSE).
 * Deploy this on your Lightsail instance to provide remote access to deployment tools.
 * 
 * Usage:
 *   node server.js [--port PORT] [--host HOST]
 * 
 * Environment Variables:
 *   PORT - Server port (default: 3000)
 *   HOST - Server host (default: 0.0.0.0)
 *   MCP_AUTH_TOKEN - Optional authentication token
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import express from 'express';
import { execSync } from 'child_process';

// Parse command line arguments
const args = process.argv.slice(2);
const portIndex = args.indexOf('--port');
const hostIndex = args.indexOf('--host');

const PORT = portIndex !== -1 ? parseInt(args[portIndex + 1]) : process.env.PORT || 3000;
const HOST = hostIndex !== -1 ? args[hostIndex + 1] : process.env.HOST || '0.0.0.0';
const AUTH_TOKEN = process.env.MCP_AUTH_TOKEN;

class LightsailDeploymentServer {
  constructor() {
    this.server = new Server(
      {
        name: 'lightsail-deployment-mcp',
        version: '1.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );
    
    this.server.onerror = (error) => console.error('[MCP Error]', error);
  }

  async initialize() {
    await this.setupToolHandlers();
    return this;
  }

  async setupToolHandlers() {
    // Import tool handlers from index.js
    // For now, we'll duplicate the essential methods
    // In production, you'd want to refactor shared code into a module
    
    const { CallToolRequestSchema, ListToolsRequestSchema } = await import('@modelcontextprotocol/sdk/types.js');
    
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'setup_complete_deployment',
          description: 'Get the enhanced setup script for creating complete Lightsail deployment automation. This returns instructions and commands to run the setup script locally on your machine, not on the MCP server. Supports 6 application types (LAMP, Node.js, Python, React, Docker, Nginx) with database configuration (MySQL, PostgreSQL, none), bucket integration, GitHub OIDC setup, and comprehensive deployment automation.',
          inputSchema: {
            type: 'object',
            properties: {
              mode: { 
                type: 'string', 
                enum: ['interactive', 'auto', 'help'],
                default: 'interactive',
                description: 'Script execution mode: interactive (prompts for input), auto (uses defaults), help (show usage)'
              },
              aws_region: { 
                type: 'string', 
                default: 'us-east-1',
                description: 'AWS region for deployment (used in auto mode)'
              },
              app_version: {
                type: 'string',
                default: '1.0.0',
                description: 'Application version (used in auto mode)'
              },
            },
          },
        },
        {
          name: 'get_deployment_status',
          description: 'Check deployment status',
          inputSchema: {
            type: 'object',
            properties: {
              repo_path: { type: 'string', description: 'Repository path' },
            },
            required: ['repo_path'],
          },
        },
        {
          name: 'get_deployment_examples',
          description: 'Get example deployment configurations and GitHub Actions workflows for different application types. Returns ready-to-use configuration files and deployment examples.',
          inputSchema: {
            type: 'object',
            properties: {
              app_type: { 
                type: 'string', 
                enum: ['lamp', 'nginx', 'nodejs', 'python', 'react', 'docker', 'all'],
                default: 'all',
                description: 'Application type to get examples for, or "all" for complete overview'
              },
              include_configs: {
                type: 'boolean',
                default: true,
                description: 'Include deployment configuration files'
              },
              include_workflows: {
                type: 'boolean', 
                default: true,
                description: 'Include GitHub Actions workflow examples'
              },
            },
          },
        },
        {
          name: 'diagnose_deployment',
          description: 'Run deployment diagnostics',
          inputSchema: {
            type: 'object',
            properties: {
              repo_path: { type: 'string' },
              check_type: { type: 'string', enum: ['all', 'prerequisites', 'configuration', 'github', 'aws', 'instance'], default: 'all' },
            },
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'setup_complete_deployment':
            return await this.setupCompleteDeployment(args);
          case 'get_deployment_examples':
            return await this.getDeploymentExamples(args);
          case 'get_deployment_status':
            return await this.getDeploymentStatus(args);
          case 'diagnose_deployment':
            return await this.diagnoseDeployment(args);
          default:
            return {
              content: [{ type: 'text', text: `Tool ${name} not implemented. Available tools: setup_complete_deployment, get_deployment_examples, get_deployment_status, diagnose_deployment` }],
            };
        }
      } catch (error) {
        return {
          content: [{ type: 'text', text: `Error: ${error.message}` }],
          isError: true,
        };
      }
    });
  }

  async getDeploymentStatus(args) {
    const { repo_path } = args;
    try {
      const output = execSync('gh run list --limit 5 --json status,conclusion,name,url', {
        cwd: repo_path,
        encoding: 'utf-8',
      });
      const runs = JSON.parse(output);
      let status = '# Deployment Status\n\n';
      runs.forEach((run) => {
        const emoji = run.conclusion === 'success' ? '✅' : run.conclusion === 'failure' ? '❌' : '🔄';
        status += `${emoji} **${run.name}** - ${run.status}\n   ${run.url}\n\n`;
      });
      return { content: [{ type: 'text', text: status }] };
    } catch (error) {
      throw new Error('Failed to get deployment status');
    }
  }

  async setupCompleteDeployment(args) {
    const { mode = 'interactive', aws_region = 'us-east-1', app_version = '1.0.0' } = args;
    
    const scriptUrl = 'https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh';
    
    let instructions = `# 🚀 Complete Lightsail Deployment Setup

## Overview
The enhanced setup script provides comprehensive deployment automation with:
- **6 Application Types**: LAMP, Node.js, Python, React, Docker, Nginx
- **Universal Database Support**: MySQL, PostgreSQL, or none (available for ALL app types)
- **GitHub OIDC Integration**: Secure AWS authentication without storing credentials
- **Lightsail Bucket Storage**: Optional S3-compatible storage integration
- **Multi-OS Support**: Ubuntu, Amazon Linux, CentOS
- **Instance Sizing**: Nano (512MB) to 2XLarge (8GB RAM)
- **Automated CI/CD**: GitHub Actions workflows with reusable patterns

## 📥 Download and Run

### Method 1: Direct Download and Execute
\`\`\`bash
# Download the script
curl -O ${scriptUrl}

# Make it executable  
chmod +x setup-complete-deployment.sh

# Run the script
./setup-complete-deployment.sh`;

    if (mode === 'auto') {
      instructions += ` --auto --aws-region ${aws_region} --app-version ${app_version}`;
    } else if (mode === 'help') {
      instructions += ` --help`;
    }

    instructions += `
\`\`\`

### Method 2: Direct Execution (No Download)
\`\`\`bash
# Run directly from GitHub
bash <(curl -s ${scriptUrl})`;

    if (mode === 'auto') {
      instructions += ` --auto --aws-region ${aws_region} --app-version ${app_version}`;
    } else if (mode === 'help') {
      instructions += ` --help`;
    }

    instructions += `
\`\`\`

## 🎯 Script Modes

### Interactive Mode (Default)
- Guided setup with prompts for all configuration options
- Application type selection with detailed descriptions
- Database configuration for all application types
- Instance sizing and OS selection
- GitHub repository creation and OIDC setup
- Best for first-time users and custom configurations

### Auto Mode
- Uses sensible defaults for rapid deployment
- Minimal prompts for essential information only
- Ideal for CI/CD pipelines and batch deployments
- Add \`--auto\` flag

### Help Mode  
- Shows comprehensive usage information and examples
- Lists all supported application types and features
- Add \`--help\` flag

## 🛠️ What the Script Creates

1. **Deployment Configuration**: \`deployment-{type}.config.yml\`
   - AWS Lightsail instance configuration
   - Database connection settings
   - Application-specific deployment steps
   - Health check and monitoring configuration

2. **GitHub Actions Workflow**: \`.github/workflows/deploy-{type}.yml\`
   - Uses the proven deploy-generic-reusable.yml pattern
   - Secure OIDC authentication with AWS
   - Automated testing and deployment pipeline
   - Artifact management and retention

3. **Example Application**: \`example-{type}-app/\` directory
   - Production-ready starter code
   - Database integration examples
   - Docker configurations (where applicable)
   - Documentation and deployment guides

4. **AWS IAM Role**: GitHub OIDC role (if needed)
   - Secure authentication without storing AWS credentials
   - Least-privilege permissions for Lightsail operations
   - Automatic role creation and configuration

## 🔧 Prerequisites

Ensure you have these installed on your local machine:
- **Git**: Version control system
- **GitHub CLI**: \`gh auth login\` (authenticated)
- **AWS CLI**: \`aws configure\` (configured with appropriate permissions)
- **Bash**: Compatible shell (bash 3.x+ supported)

## 📋 Supported Application Types

### LAMP Stack
- **Tech Stack**: Linux + Apache + MySQL/PostgreSQL + PHP
- **Features**: Database integration, file uploads, admin panel
- **Use Cases**: Content management, web applications, APIs

### Node.js
- **Tech Stack**: Node.js + Express + MySQL/PostgreSQL
- **Features**: REST APIs, real-time applications, microservices
- **Use Cases**: Backend services, API servers, full-stack apps

### Python
- **Tech Stack**: Python + Flask + MySQL/PostgreSQL + Gunicorn
- **Features**: Web frameworks, database ORM, API development
- **Use Cases**: Web applications, data processing, machine learning APIs

### React
- **Tech Stack**: React + Build optimization + Optional backend integration
- **Features**: Single-page applications, static site generation
- **Use Cases**: Frontend applications, dashboards, progressive web apps

### Docker
- **Tech Stack**: Multi-container applications with docker-compose
- **Features**: Microservices architecture, database containers
- **Use Cases**: Complex applications, development environments, scalable services

### Nginx
- **Tech Stack**: Nginx + Static files + Reverse proxy
- **Features**: High-performance static serving, load balancing
- **Use Cases**: Static websites, reverse proxy, load balancer

## 🗄️ Database Configuration

**Available for ALL Application Types:**
- **MySQL**: Popular relational database with excellent PHP/Node.js support
- **PostgreSQL**: Advanced relational database with JSON support
- **None**: Skip database setup for static sites or external database usage

**Database Features:**
- Automatic database creation and user setup
- Environment variable configuration
- Connection pooling and optimization
- Backup and maintenance scripts

## 🎉 After Running the Script

1. **Review Generated Files**: Check deployment configuration and workflow files
2. **Update Credentials**: Change default passwords in deployment config
3. **Customize Application**: Modify the example app for your needs
4. **Push to GitHub**: Commit and push to trigger first deployment
5. **Monitor Deployment**: Watch GitHub Actions for deployment progress
6. **Access Application**: Use the Lightsail instance public IP

## 🔍 Troubleshooting

- **Prerequisites Check**: Script validates all required tools
- **GitHub Authentication**: Ensures \`gh auth status\` is successful
- **AWS Configuration**: Verifies \`aws sts get-caller-identity\` works
- **Repository Creation**: Handles existing repositories gracefully
- **OIDC Role Setup**: Creates IAM roles with proper trust policies

## 🆘 Need Help?

- **Script Help**: Run with \`--help\` flag for detailed usage
- **Generated Documentation**: Check README files in created directories
- **Repository Issues**: https://github.com/naveenraj44125-creator/lamp-stack-lightsail/issues
- **Example Applications**: Review working examples in the repository

---
**Important**: This script runs entirely on your local machine and creates files in your current directory. It does not install anything on the MCP server. All AWS operations are performed through your local AWS CLI configuration.`;

    return {
      content: [{ type: 'text', text: instructions }]
    };
  }

  async getDeploymentExamples(args) {
    const { app_type = 'all', include_configs = true, include_workflows = true } = args;
    
    const baseUrl = 'https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main';
    
    let examples = `# 📚 Deployment Examples and Configurations

## Available Application Types
- **LAMP**: PHP with Apache, MySQL/PostgreSQL support
- **Node.js**: Express applications with PM2, database support  
- **Python**: Flask/Django applications with Gunicorn, database support
- **React**: Frontend applications with build optimization
- **Docker**: Containerized applications with docker-compose
- **Nginx**: Static sites and reverse proxy configurations

`;

    const appTypes = app_type === 'all' ? ['lamp', 'nodejs', 'python', 'react', 'docker', 'nginx'] : [app_type];
    
    for (const type of appTypes) {
      examples += `## ${type.toUpperCase()} Application

`;
      
      if (include_configs) {
        examples += `### 📄 Deployment Configuration
\`\`\`bash
# Download ${type} deployment config
curl -O ${baseUrl}/deployment-${type}.config.yml
\`\`\`

`;
      }
      
      if (include_workflows) {
        examples += `### ⚙️ GitHub Actions Workflow  
\`\`\`bash
# Download ${type} workflow
mkdir -p .github/workflows
curl -o .github/workflows/deploy-${type}.yml ${baseUrl}/.github/workflows/deploy-${type}.yml
\`\`\`

`;
      }
      
      examples += `### 📁 Example Application
\`\`\`bash
# Download complete ${type} example
git clone ${baseUrl.replace('/raw/', '/')} temp-repo
cp -r temp-repo/example-${type}-app ./
rm -rf temp-repo
\`\`\`

### 🔗 Direct Links
- **Config**: [deployment-${type}.config.yml](${baseUrl}/deployment-${type}.config.yml)
- **Workflow**: [deploy-${type}.yml](${baseUrl}/.github/workflows/deploy-${type}.yml)  
- **Example**: [example-${type}-app/](${baseUrl.replace('/raw/', '/tree/')}/example-${type}-app)

---

`;
    }

    examples += `## 🚀 Quick Start

1. **Use the Complete Setup Script** (Recommended):
   \`\`\`bash
   curl -O ${baseUrl}/setup-complete-deployment.sh
   chmod +x setup-complete-deployment.sh
   ./setup-complete-deployment.sh
   \`\`\`

2. **Manual Setup**:
   - Download desired configuration and workflow files
   - Copy example application as starting point
   - Customize configuration for your needs
   - Commit and push to trigger deployment

## 📖 Documentation

- **Main Repository**: https://github.com/naveenraj44125-creator/lamp-stack-lightsail
- **Setup Guide**: [README.md](${baseUrl}/README.md)
- **MCP Server**: [mcp-server/README.md](${baseUrl}/mcp-server/README.md)

---
**Note**: All files are downloaded to your local machine. No installation occurs on the MCP server.`;

    return {
      content: [{ type: 'text', text: examples }]
    };
  }

  async diagnoseDeployment(args) {
    const { repo_path = '.', check_type = 'all' } = args;
    let report = '# 🔍 Deployment Diagnostics\n\n';
    
    report += '## Prerequisites Check\n\n';
    
    // Check Git
    try {
      const gitVersion = execSync('git --version', { encoding: 'utf-8' }).trim();
      report += `✅ **Git**: ${gitVersion}\n`;
    } catch (error) {
      report += '❌ **Git**: Not installed or not in PATH\n';
    }

    // Check GitHub CLI
    try {
      const ghVersion = execSync('gh --version', { encoding: 'utf-8' }).trim().split('\n')[0];
      report += `✅ **GitHub CLI**: ${ghVersion}\n`;
      
      try {
        execSync('gh auth status', { encoding: 'utf-8', stdio: 'pipe' });
        report += '✅ **GitHub Auth**: Authenticated\n';
      } catch (authError) {
        report += '❌ **GitHub Auth**: Not authenticated (run `gh auth login`)\n';
      }
    } catch (error) {
      report += '❌ **GitHub CLI**: Not installed\n';
    }

    // Check AWS CLI
    try {
      const awsVersion = execSync('aws --version', { encoding: 'utf-8' }).trim();
      report += `✅ **AWS CLI**: ${awsVersion}\n`;
      
      try {
        const identity = execSync('aws sts get-caller-identity', { encoding: 'utf-8' });
        const identityData = JSON.parse(identity);
        report += `✅ **AWS Auth**: Configured (Account: ${identityData.Account})\n`;
      } catch (authError) {
        report += '❌ **AWS Auth**: Not configured (run `aws configure`)\n';
      }
    } catch (error) {
      report += '❌ **AWS CLI**: Not installed\n';
    }

    // Check Node.js (optional)
    try {
      const nodeVersion = execSync('node --version', { encoding: 'utf-8' }).trim();
      report += `✅ **Node.js**: ${nodeVersion}\n`;
    } catch (error) {
      report += '⚠️  **Node.js**: Not installed (required for Node.js applications)\n';
    }

    // Check repository status if in a git repo
    report += '\n## Repository Status\n\n';
    try {
      execSync('git rev-parse --git-dir', { cwd: repo_path, stdio: 'pipe' });
      
      try {
        const branch = execSync('git branch --show-current', { cwd: repo_path, encoding: 'utf-8' }).trim();
        report += `✅ **Current Branch**: ${branch}\n`;
      } catch (error) {
        report += '⚠️  **Current Branch**: Unable to determine\n';
      }
      
      try {
        const status = execSync('git status --porcelain', { cwd: repo_path, encoding: 'utf-8' });
        if (status.trim()) {
          report += '⚠️  **Working Directory**: Has uncommitted changes\n';
        } else {
          report += '✅ **Working Directory**: Clean\n';
        }
      } catch (error) {
        report += '⚠️  **Working Directory**: Unable to check status\n';
      }
      
      try {
        const remote = execSync('git remote get-url origin', { cwd: repo_path, encoding: 'utf-8' }).trim();
        report += `✅ **Remote Origin**: ${remote}\n`;
      } catch (error) {
        report += '❌ **Remote Origin**: Not configured\n';
      }
    } catch (error) {
      report += '❌ **Git Repository**: Not in a git repository\n';
    }

    // Check for deployment files
    report += '\n## Deployment Configuration\n\n';
    const configFiles = ['deployment-lamp.config.yml', 'deployment-nodejs.config.yml', 'deployment-python.config.yml', 'deployment-react.config.yml', 'deployment-docker.config.yml', 'deployment-nginx.config.yml'];
    let foundConfigs = 0;
    
    configFiles.forEach(file => {
      try {
        execSync(`test -f ${file}`, { cwd: repo_path, stdio: 'pipe' });
        report += `✅ **${file}**: Found\n`;
        foundConfigs++;
      } catch (error) {
        // File doesn't exist, don't report as error
      }
    });
    
    if (foundConfigs === 0) {
      report += '⚠️  **Deployment Configs**: No deployment configuration files found\n';
    }

    // Check for GitHub Actions workflows
    try {
      const workflows = execSync('ls .github/workflows/*.yml 2>/dev/null || true', { cwd: repo_path, encoding: 'utf-8' }).trim();
      if (workflows) {
        const workflowCount = workflows.split('\n').filter(w => w.trim()).length;
        report += `✅ **GitHub Actions**: ${workflowCount} workflow(s) found\n`;
      } else {
        report += '⚠️  **GitHub Actions**: No workflows found\n';
      }
    } catch (error) {
      report += '⚠️  **GitHub Actions**: Unable to check workflows\n';
    }

    report += '\n## 🚀 Next Steps\n\n';
    report += '1. **Install Missing Tools**: Install any missing prerequisites\n';
    report += '2. **Authenticate Services**: Run `gh auth login` and `aws configure` if needed\n';
    report += '3. **Run Setup Script**: Use `setup_complete_deployment` tool to create deployment automation\n';
    report += '4. **Test Deployment**: Push changes to trigger GitHub Actions workflow\n';

    return { content: [{ type: 'text', text: report }] };
  }

  async connect(transport) {
    await this.server.connect(transport);
  }
}

// Create Express app
const app = express();

// Root endpoint - landing page
app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lightsail Deployment MCP Server</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 800px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .status {
            display: inline-block;
            padding: 8px 16px;
            background: #10b981;
            color: white;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        .section {
            margin: 30px 0;
        }
        .section h2 {
            color: #333;
            font-size: 20px;
            margin-bottom: 15px;
        }
        .endpoint {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
        }
        .endpoint strong {
            color: #667eea;
        }
        .tools {
            display: grid;
            gap: 10px;
            margin-top: 15px;
        }
        .tool {
            background: #f0f0f0;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .tool strong {
            color: #667eea;
        }
        .config {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 600;
            margin: 10px 10px 10px 0;
            transition: transform 0.2s;
        }
        .button:hover {
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Lightsail Deployment MCP Server</h1>
        <span class="status">✓ Online</span>
        
        <div class="section">
            <h2>📡 Endpoints</h2>
            <div class="endpoint"><strong>GET</strong> /health - Health check</div>
            <div class="endpoint"><strong>GET</strong> /sse - MCP SSE endpoint</div>
            <div class="endpoint"><strong>POST</strong> /message - MCP message endpoint</div>
        </div>

        <div class="section">
            <h2>🛠️ Available Tools</h2>
            <div class="tools">
                <div class="tool">
                    <strong>setup_complete_deployment</strong><br>
                    Get the enhanced setup script for complete deployment automation.<br>
                    <em>Supports 6 app types (LAMP, Node.js, Python, React, Docker, Nginx) with universal database support, GitHub OIDC, and bucket integration. Features interactive mode, auto mode, and help mode. Creates deployment configuration, GitHub Actions workflow, and example application on your local machine.</em>
                </div>
                <div class="tool">
                    <strong>get_deployment_examples</strong><br>
                    Get example configurations and workflows for different application types.<br>
                    <em>Ready-to-use deployment configs, GitHub Actions workflows, and starter applications. Downloads to your local machine, not the MCP server.</em>
                </div>
                <div class="tool">
                    <strong>get_deployment_status</strong><br>
                    Check deployment status and GitHub Actions workflow runs.<br>
                    <em>Monitor active deployments and view recent workflow execution results</em>
                </div>
                <div class="tool">
                    <strong>diagnose_deployment</strong><br>
                    Run comprehensive deployment diagnostics and troubleshooting.<br>
                    <em>Check prerequisites, repository status, configuration files, and provide next steps. All checks run on your local machine.</em>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>⚙️ Client Configuration</h2>
            <p style="margin-bottom: 15px;">Add this to your MCP client (Claude Desktop, Amazon Q, etc.):</p>
            <div class="config">{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://${req.hostname}:${PORT}/sse",
      "transport": "sse"
    }
  }
}</div>
        </div>

        <div class="section">
            <a href="/health" class="button">Health Check</a>
            <a href="https://github.com/naveenraj44125-creator/lamp-stack-lightsail/tree/main/mcp-server" class="button">Documentation</a>
        </div>
    </div>
</body>
</html>
  `);
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'lightsail-deployment-mcp', version: '1.1.0' });
});

// Authentication middleware
const authenticate = (req, res, next) => {
  if (!AUTH_TOKEN) {
    return next(); // No auth required if token not set
  }

  const token = req.headers.authorization?.replace('Bearer ', '');
  if (token !== AUTH_TOKEN) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
};

// Store active sessions
const sessions = new Map();

// SSE endpoint for MCP
app.get('/sse', authenticate, async (req, res) => {
  console.log('New SSE connection from', req.ip);

  const transport = new SSEServerTransport('/message', res);
  const mcpServer = await new LightsailDeploymentServer().initialize();
  
  // Store session
  const sessionId = transport.sessionId;
  sessions.set(sessionId, { transport, mcpServer });
  
  await mcpServer.connect(transport);

  req.on('close', () => {
    console.log('SSE connection closed');
    sessions.delete(sessionId);
  });
});

// Message endpoint for MCP - must be before express.json() middleware
app.post('/message', authenticate, async (req, res) => {
  const sessionId = req.query.sessionId;
  const session = sessions.get(sessionId);
  
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  try {
    await session.transport.handlePostMessage(req, res);
  } catch (error) {
    console.error('Error handling message:', error);
    if (!res.headersSent) {
      res.status(500).json({ error: error.message });
    }
  }
});

// Start server
app.listen(PORT, HOST, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  Lightsail Deployment MCP Server (HTTP/SSE)                ║
╠════════════════════════════════════════════════════════════╣
║  Status: Running                                           ║
║  Host: ${HOST.padEnd(50)}║
║  Port: ${String(PORT).padEnd(50)}║
║  Auth: ${(AUTH_TOKEN ? 'Enabled' : 'Disabled').padEnd(50)}║
╠════════════════════════════════════════════════════════════╣
║  Endpoints:                                                ║
║    GET  /health  - Health check                           ║
║    GET  /sse     - MCP SSE endpoint                       ║
║    POST /message - MCP message endpoint                   ║
╠════════════════════════════════════════════════════════════╣
║  Client Configuration:                                     ║
║    {                                                       ║
║      "mcpServers": {                                       ║
║        "lightsail-deployment": {                           ║
║          "url": "http://${HOST === '0.0.0.0' ? 'YOUR_IP' : HOST}:${PORT}/sse"${AUTH_TOKEN ? ',          ║' : ''}
${AUTH_TOKEN ? `║          "headers": {                                      ║
║            "Authorization": "Bearer YOUR_TOKEN"            ║
║          }                                                 ║` : '║                                                        ║'}
║        }                                                   ║
║      }                                                     ║
║    }                                                       ║
╚════════════════════════════════════════════════════════════╝
  `);

  if (!AUTH_TOKEN) {
    console.log('⚠️  WARNING: No authentication token set!');
    console.log('   Set MCP_AUTH_TOKEN environment variable for security.');
    console.log('   Example: MCP_AUTH_TOKEN=your-secret-token node server.js\n');
  }
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\nShutting down gracefully...');
  process.exit(0);
});
