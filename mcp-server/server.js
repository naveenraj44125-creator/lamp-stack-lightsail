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
          description: 'Get the enhanced setup script for creating complete Lightsail deployment automation. This returns instructions and commands to run the setup script locally on your machine, not on the MCP server. Supports 6 application types (LAMP, Node.js, Python, React, Docker, Nginx) with database configuration (MySQL, PostgreSQL, none), bucket integration, GitHub OIDC setup, and comprehensive deployment automation. In automated mode, AI agents can specify all deployment requirements without interactive prompts.',
          inputSchema: {
            type: 'object',
            properties: {
              mode: { 
                type: 'string', 
                enum: ['interactive', 'auto', 'help', 'fully_automated'],
                default: 'interactive',
                description: 'Script execution mode: interactive (prompts for input), auto (uses defaults with some prompts), fully_automated (AI agent provides all parameters), help (show usage)'
              },
              aws_region: { 
                type: 'string', 
                default: 'us-east-1',
                description: 'AWS region for deployment'
              },
              app_version: {
                type: 'string',
                default: '1.0.0',
                description: 'Application version'
              },
              app_type: {
                type: 'string',
                enum: ['lamp', 'nodejs', 'python', 'react', 'docker', 'nginx'],
                description: 'Application type (required for fully_automated mode)'
              },
              app_name: {
                type: 'string',
                description: 'Application name (defaults to {app_type}-app if not provided)'
              },
              instance_name: {
                type: 'string',
                description: 'Lightsail instance name (defaults to {app_type}-app-{timestamp} if not provided)'
              },
              blueprint_id: {
                type: 'string',
                enum: ['ubuntu_22_04', 'ubuntu_20_04', 'amazon_linux_2023'],
                default: 'ubuntu_22_04',
                description: 'Operating system blueprint'
              },
              bundle_id: {
                type: 'string',
                enum: ['nano_3_0', 'micro_3_0', 'small_3_0', 'medium_3_0', 'large_3_0'],
                default: 'micro_3_0',
                description: 'Instance size bundle (Docker apps need minimum small_3_0)'
              },
              database_type: {
                type: 'string',
                enum: ['mysql', 'postgresql', 'none'],
                default: 'none',
                description: 'Database type (available for all application types)'
              },
              db_external: {
                type: 'boolean',
                default: false,
                description: 'Use external RDS database instead of local database'
              },
              db_rds_name: {
                type: 'string',
                description: 'RDS instance name (required if db_external is true)'
              },
              db_name: {
                type: 'string',
                default: 'app_db',
                description: 'Database name'
              },
              enable_bucket: {
                type: 'boolean',
                default: false,
                description: 'Enable Lightsail bucket for S3-compatible storage'
              },
              bucket_name: {
                type: 'string',
                description: 'Bucket name (required if enable_bucket is true)'
              },
              bucket_access: {
                type: 'string',
                enum: ['read_only', 'read_write'],
                default: 'read_write',
                description: 'Bucket access level'
              },
              bucket_bundle: {
                type: 'string',
                enum: ['small_1_0', 'medium_1_0', 'large_1_0'],
                default: 'small_1_0',
                description: 'Bucket size bundle'
              },
              github_repo: {
                type: 'string',
                description: 'GitHub repository name (defaults to {app_name} if not provided)'
              },
              repo_visibility: {
                type: 'string',
                enum: ['public', 'private'],
                default: 'private',
                description: 'GitHub repository visibility'
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
    const { 
      mode = 'interactive', 
      aws_region = 'us-east-1', 
      app_version = '1.0.0',
      app_type,
      app_name,
      instance_name,
      blueprint_id = 'ubuntu_22_04',
      bundle_id = 'micro_3_0',
      database_type = 'none',
      db_external = false,
      db_rds_name,
      db_name = 'app_db',
      enable_bucket = false,
      bucket_name,
      bucket_access = 'read_write',
      bucket_bundle = 'small_1_0',
      github_repo,
      repo_visibility = 'private'
    } = args;
    
    const scriptUrl = 'https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh';
    
    // Validate required parameters for fully_automated mode
    if (mode === 'fully_automated') {
      if (!app_type) {
        return {
          content: [{ type: 'text', text: '❌ Error: app_type is required for fully_automated mode. Choose from: lamp, nodejs, python, react, docker, nginx' }],
          isError: true,
        };
      }
      
      if (enable_bucket && !bucket_name) {
        return {
          content: [{ type: 'text', text: '❌ Error: bucket_name is required when enable_bucket is true' }],
          isError: true,
        };
      }
      
      if (db_external && !db_rds_name) {
        return {
          content: [{ type: 'text', text: '❌ Error: db_rds_name is required when db_external is true' }],
          isError: true,
        };
      }
      
      // Validate bundle size for Docker applications
      if (app_type === 'docker' && ['nano_3_0', 'micro_3_0'].includes(bundle_id)) {
        return {
          content: [{ type: 'text', text: '❌ Error: Docker applications require minimum small_3_0 bundle (2GB RAM). Current bundle: ' + bundle_id }],
          isError: true,
        };
      }
    }
    
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
    } else if (mode === 'fully_automated') {
      // Generate environment variables for fully automated execution
      const timestamp = Date.now();
      const finalAppName = app_name || `${app_type}-app`;
      const finalInstanceName = instance_name || `${app_type}-app-${timestamp}`;
      const finalGithubRepo = github_repo || finalAppName;
      const finalBucketName = enable_bucket ? (bucket_name || `${app_type}-bucket-${timestamp}`) : '';
      const finalDbRdsName = db_external ? (db_rds_name || `${app_type}-${database_type}-db`) : '';
      
      instructions += ` --auto --aws-region ${aws_region} --app-version ${app_version}`;
      
      // Add environment variables for fully automated mode
      instructions = instructions.replace('# Run the script\n./setup-complete-deployment.sh', 
        `# Set environment variables for fully automated deployment
export AUTO_MODE=true
export AWS_REGION="${aws_region}"
export APP_VERSION="${app_version}"
export APP_TYPE="${app_type}"
export APP_NAME="${finalAppName}"
export INSTANCE_NAME="${finalInstanceName}"
export BLUEPRINT_ID="${blueprint_id}"
export BUNDLE_ID="${bundle_id}"
export DATABASE_TYPE="${database_type}"
export DB_EXTERNAL="${db_external}"
export DB_RDS_NAME="${finalDbRdsName}"
export DB_NAME="${db_name}"
export ENABLE_BUCKET="${enable_bucket}"
export BUCKET_NAME="${finalBucketName}"
export BUCKET_ACCESS="${bucket_access}"
export BUCKET_BUNDLE="${bucket_bundle}"
export GITHUB_REPO="${finalGithubRepo}"
export REPO_VISIBILITY="${repo_visibility}"

# Run the script in fully automated mode
./setup-complete-deployment.sh`);
    }

    instructions += `
\`\`\`

### Method 2: Direct Execution (No Download)
\`\`\`bash`;

    if (mode === 'fully_automated') {
      // For direct execution, we need to set environment variables inline
      const timestamp = Date.now();
      const finalAppName = app_name || `${app_type}-app`;
      const finalInstanceName = instance_name || `${app_type}-app-${timestamp}`;
      const finalGithubRepo = github_repo || finalAppName;
      const finalBucketName = enable_bucket ? (bucket_name || `${app_type}-bucket-${timestamp}`) : '';
      const finalDbRdsName = db_external ? (db_rds_name || `${app_type}-${database_type}-db`) : '';
      
      instructions += `# Run directly from GitHub with environment variables
AUTO_MODE=true AWS_REGION="${aws_region}" APP_VERSION="${app_version}" \\
APP_TYPE="${app_type}" APP_NAME="${finalAppName}" INSTANCE_NAME="${finalInstanceName}" \\
BLUEPRINT_ID="${blueprint_id}" BUNDLE_ID="${bundle_id}" DATABASE_TYPE="${database_type}" \\
DB_EXTERNAL="${db_external}" DB_RDS_NAME="${finalDbRdsName}" DB_NAME="${db_name}" \\
ENABLE_BUCKET="${enable_bucket}" BUCKET_NAME="${finalBucketName}" BUCKET_ACCESS="${bucket_access}" \\
BUCKET_BUNDLE="${bucket_bundle}" GITHUB_REPO="${finalGithubRepo}" REPO_VISIBILITY="${repo_visibility}" \\
bash <(curl -s ${scriptUrl}) --auto --aws-region ${aws_region} --app-version ${app_version}`;
    } else {
      instructions += `# Run directly from GitHub
bash <(curl -s ${scriptUrl})`;
      
      if (mode === 'auto') {
        instructions += ` --auto --aws-region ${aws_region} --app-version ${app_version}`;
      } else if (mode === 'help') {
        instructions += ` --help`;
      }
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

### Fully Automated Mode (AI Agent Mode)
- **Zero prompts** - AI agents provide all parameters via environment variables
- Complete deployment automation without human intervention
- Validates all parameters before execution
- Perfect for AI-driven deployment workflows
- All configuration specified via environment variables

### Help Mode  
- Shows comprehensive usage information and examples
- Lists all supported application types and features
- Add \`--help\` flag

${mode === 'fully_automated' ? `
## 🤖 AI Agent Configuration Summary

**Deployment Configuration:**
- **Application Type**: ${app_type}
- **Application Name**: ${app_name || `${app_type}-app`}
- **Instance Name**: ${instance_name || `${app_type}-app-${Date.now()}`}
- **AWS Region**: ${aws_region}
- **Operating System**: ${blueprint_id}
- **Instance Size**: ${bundle_id}
- **App Version**: ${app_version}

**Database Configuration:**
- **Database Type**: ${database_type}
- **External RDS**: ${db_external ? 'Yes' : 'No'}
${db_external ? `- **RDS Instance**: ${db_rds_name || `${app_type}-${database_type}-db`}` : ''}
- **Database Name**: ${db_name}

**Storage Configuration:**
- **Bucket Enabled**: ${enable_bucket ? 'Yes' : 'No'}
${enable_bucket ? `- **Bucket Name**: ${bucket_name || `${app_type}-bucket-${Date.now()}`}
- **Bucket Access**: ${bucket_access}
- **Bucket Size**: ${bucket_bundle}` : ''}

**GitHub Configuration:**
- **Repository**: ${github_repo || app_name || `${app_type}-app`}
- **Visibility**: ${repo_visibility}

**Validation Results:**
✅ All required parameters provided
✅ Configuration validated successfully
${app_type === 'docker' && ['nano_3_0', 'micro_3_0'].includes(bundle_id) ? 
  '⚠️  Warning: Docker applications work better with small_3_0+ bundles' : 
  '✅ Bundle size appropriate for application type'}
` : ''}`

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
