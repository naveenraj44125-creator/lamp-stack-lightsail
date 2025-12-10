#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { execSync } from 'child_process';
import { writeFileSync, existsSync } from 'fs';
import { join } from 'path';

const REPO_URL = 'https://github.com/naveenraj44125-creator/lamp-stack-lightsail.git';

class LightsailDeploymentServer {
  constructor() {
    this.server = new Server(
      {
        name: 'lightsail-deployment-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'setup_new_repository',
          description: 'Create a new GitHub repository with Lightsail deployment automation. Supports multiple operating systems (Ubuntu, Amazon Linux, CentOS) and instance sizes (Nano to 2XLarge). Sets up workflows, OIDC, and deployment configuration.',
          inputSchema: {
            type: 'object',
            properties: {
              repo_name: {
                type: 'string',
                description: 'Name of the new repository',
              },
              app_type: {
                type: 'string',
                enum: ['lamp', 'nginx', 'nodejs', 'python', 'react', 'docker'],
                description: 'Application type to deploy',
              },
              instance_name: {
                type: 'string',
                description: 'Lightsail instance name',
              },
              aws_region: {
                type: 'string',
                default: 'us-east-1',
                description: 'AWS region for deployment',
              },
              blueprint_id: {
                type: 'string',
                description: 'Operating system blueprint (ubuntu_22_04, ubuntu_20_04, amazon_linux_2023, amazon_linux_2, centos_7_2009_01)',
                enum: ['ubuntu_22_04', 'ubuntu_20_04', 'amazon_linux_2023', 'amazon_linux_2', 'centos_7_2009_01'],
                default: 'ubuntu_22_04',
              },
              bundle_id: {
                type: 'string',
                description: 'Instance size bundle (nano_3_0, micro_3_0, small_3_0, medium_3_0, large_3_0, xlarge_3_0, 2xlarge_3_0)',
                enum: ['nano_3_0', 'micro_3_0', 'small_3_0', 'medium_3_0', 'large_3_0', 'xlarge_3_0', '2xlarge_3_0'],
                default: 'small_3_0',
              },
              enable_bucket: {
                type: 'boolean',
                default: false,
                description: 'Enable S3 bucket integration',
              },
              bucket_name: {
                type: 'string',
                description: 'S3 bucket name (if enable_bucket is true)',
              },
              database_type: {
                type: 'string',
                enum: ['none', 'mysql', 'postgresql'],
                default: 'none',
                description: 'Database type',
              },
              use_rds: {
                type: 'boolean',
                default: false,
                description: 'Use AWS RDS for database',
              },
            },
            required: ['repo_name', 'app_type', 'instance_name'],
          },
        },
        {
          name: 'integrate_existing_repository',
          description: 'Add Lightsail deployment automation to an existing GitHub repository. Supports multiple operating systems (Ubuntu, Amazon Linux, CentOS) and instance sizes (Nano to 2XLarge). Interactive configuration for OS, instance size, and application type.',
          inputSchema: {
            type: 'object',
            properties: {
              repo_path: {
                type: 'string',
                description: 'Path to existing repository',
              },
              app_type: {
                type: 'string',
                enum: ['lamp', 'nginx', 'nodejs', 'python', 'react', 'docker'],
                description: 'Application type',
              },
              instance_name: {
                type: 'string',
                description: 'Lightsail instance name',
              },
              aws_region: {
                type: 'string',
                default: 'us-east-1',
                description: 'AWS region',
              },
              blueprint_id: {
                type: 'string',
                description: 'Operating system blueprint (ubuntu_22_04, ubuntu_20_04, amazon_linux_2023, amazon_linux_2, centos_7_2009_01)',
                enum: ['ubuntu_22_04', 'ubuntu_20_04', 'amazon_linux_2023', 'amazon_linux_2', 'centos_7_2009_01'],
                default: 'ubuntu_22_04',
              },
              bundle_id: {
                type: 'string',
                description: 'Instance size bundle (nano_3_0, micro_3_0, small_3_0, medium_3_0, large_3_0, xlarge_3_0, 2xlarge_3_0)',
                enum: ['nano_3_0', 'micro_3_0', 'small_3_0', 'medium_3_0', 'large_3_0', 'xlarge_3_0', '2xlarge_3_0'],
                default: 'small_3_0',
              },
              enable_bucket: {
                type: 'boolean',
                default: false,
                description: 'Enable S3 bucket',
              },
            },
            required: ['repo_path', 'app_type', 'instance_name'],
          },
        },
        {
          name: 'generate_deployment_config',
          description: 'Generate a deployment configuration file for Lightsail with OS and instance size selection',
          inputSchema: {
            type: 'object',
            properties: {
              app_type: {
                type: 'string',
                enum: ['lamp', 'nginx', 'nodejs', 'python', 'react', 'docker'],
                description: 'Application type',
              },
              instance_name: {
                type: 'string',
                description: 'Instance name',
              },
              blueprint_id: {
                type: 'string',
                description: 'Operating system blueprint (ubuntu_22_04, ubuntu_20_04, amazon_linux_2023, amazon_linux_2, centos_7_2009_01)',
                enum: ['ubuntu_22_04', 'ubuntu_20_04', 'amazon_linux_2023', 'amazon_linux_2', 'centos_7_2009_01'],
                default: 'ubuntu_22_04',
              },
              bundle_id: {
                type: 'string',
                description: 'Instance size bundle (nano_3_0, micro_3_0, small_3_0, medium_3_0, large_3_0, xlarge_3_0, 2xlarge_3_0)',
                enum: ['nano_3_0', 'micro_3_0', 'small_3_0', 'medium_3_0', 'large_3_0', 'xlarge_3_0', '2xlarge_3_0'],
                default: 'small_3_0',
              },
              dependencies: {
                type: 'array',
                items: { type: 'string' },
                description: 'Additional dependencies (redis, git, etc.)',
              },
              enable_bucket: {
                type: 'boolean',
                default: false,
              },
              bucket_config: {
                type: 'object',
                properties: {
                  name: { type: 'string' },
                  access_level: { type: 'string', enum: ['read_only', 'read_write'] },
                  bundle_id: { type: 'string', enum: ['small_1_0', 'medium_1_0', 'large_1_0'] },
                },
              },
            },
            required: ['app_type', 'instance_name'],
          },
        },
        {
          name: 'setup_oidc_authentication',
          description: 'Set up GitHub Actions OIDC authentication with AWS',
          inputSchema: {
            type: 'object',
            properties: {
              repo_owner: {
                type: 'string',
                description: 'GitHub repository owner',
              },
              repo_name: {
                type: 'string',
                description: 'GitHub repository name',
              },
              role_name: {
                type: 'string',
                description: 'IAM role name to create',
              },
              trust_branch: {
                type: 'string',
                default: 'main',
                description: 'Branch to trust for deployments',
              },
            },
            required: ['repo_owner', 'repo_name', 'role_name'],
          },
        },
        {
          name: 'get_deployment_status',
          description: 'Check the status of Lightsail deployments',
          inputSchema: {
            type: 'object',
            properties: {
              repo_path: {
                type: 'string',
                description: 'Path to repository',
              },
            },
            required: ['repo_path'],
          },
        },
        {
          name: 'list_available_examples',
          description: 'List all available example applications and their features',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'diagnose_deployment',
          description: 'Run diagnostics to troubleshoot deployment issues. Checks prerequisites, configuration, and common problems.',
          inputSchema: {
            type: 'object',
            properties: {
              repo_path: {
                type: 'string',
                description: 'Path to repository (optional, defaults to current directory)',
              },
              check_type: {
                type: 'string',
                enum: ['all', 'prerequisites', 'configuration', 'github', 'aws', 'instance'],
                default: 'all',
                description: 'Type of diagnostic check to run',
              },
            },
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'setup_new_repository':
            return await this.setupNewRepository(args);
          case 'integrate_existing_repository':
            return await this.integrateExistingRepository(args);
          case 'generate_deployment_config':
            return await this.generateDeploymentConfig(args);
          case 'setup_oidc_authentication':
            return await this.setupOIDC(args);
          case 'get_deployment_status':
            return await this.getDeploymentStatus(args);
          case 'list_available_examples':
            return await this.listExamples();
          case 'diagnose_deployment':
            return await this.diagnoseDeployment(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async setupNewRepository(args) {
    const {
      repo_name,
      app_type,
      instance_name,
      aws_region = 'us-east-1',
      blueprint_id = 'ubuntu_22_04',
      bundle_id = 'small_3_0',
      enable_bucket = false,
      bucket_name,
      database_type = 'none',
      use_rds = false,
    } = args;

    // Clone the template repository
    const tempDir = `/tmp/lightsail-${Date.now()}`;
    execSync(`git clone ${REPO_URL} ${tempDir}`, { stdio: 'pipe' });

    // Generate configuration
    const config = this.generateConfig({
      app_type,
      instance_name,
      aws_region,
      blueprint_id,
      bundle_id,
      enable_bucket,
      bucket_name,
      database_type,
      use_rds,
    });

    // Create deployment config file
    const configPath = join(tempDir, `deployment-${app_type}.config.yml`);
    writeFileSync(configPath, config);

    return {
      content: [
        {
          type: 'text',
          text: `✅ Repository setup prepared!

**Next Steps:**
1. Create GitHub repository: gh repo create ${repo_name} --public
2. Copy files from: ${tempDir}
3. Push to GitHub
4. Set up OIDC with: setup_oidc_authentication

**Configuration Generated:**
- Instance: ${instance_name} (${bundle_id})
- Region: ${aws_region}
- OS: ${blueprint_id}
- Type: ${app_type}
- Bucket: ${enable_bucket ? 'Enabled' : 'Disabled'}
- Database: ${database_type}${use_rds ? ' (RDS)' : ''}

**Files Created:**
- .github/workflows/deploy-generic-reusable.yml
- deployment-${app_type}.config.yml
- workflows/*.py

Run deployments with: git push origin main`,
        },
      ],
    };
  }

  async integrateExistingRepository(args) {
    const { 
      repo_path, 
      app_type, 
      instance_name, 
      aws_region = 'us-east-1', 
      blueprint_id = 'ubuntu_22_04',
      bundle_id = 'small_3_0',
      enable_bucket = false 
    } = args;

    if (!existsSync(repo_path)) {
      throw new Error(`Repository path not found: ${repo_path}`);
    }

    // Clone template files
    const tempDir = `/tmp/lightsail-template-${Date.now()}`;
    execSync(`git clone ${REPO_URL} ${tempDir}`, { stdio: 'pipe' });

    // Copy workflow files
    execSync(`cp -r ${tempDir}/.github ${repo_path}/`, { stdio: 'pipe' });
    execSync(`cp -r ${tempDir}/workflows ${repo_path}/`, { stdio: 'pipe' });

    // Generate config
    const config = this.generateConfig({ 
      app_type, 
      instance_name, 
      aws_region, 
      blueprint_id, 
      bundle_id, 
      enable_bucket 
    });
    writeFileSync(join(repo_path, `deployment-${app_type}.config.yml`), config);

    return {
      content: [
        {
          type: 'text',
          text: `✅ Lightsail deployment integrated!

**Added to ${repo_path}:**
- .github/workflows/ (GitHub Actions)
- workflows/ (Python deployment scripts)
- deployment-${app_type}.config.yml

**Next Steps:**
1. Set up AWS OIDC authentication
2. Commit and push changes
3. Deployment will trigger automatically

**Test locally:**
cd ${repo_path}
git add .
git commit -m "Add Lightsail deployment"
git push origin main`,
        },
      ],
    };
  }

  async generateDeploymentConfig(args) {
    const config = this.generateConfig(args);

    return {
      content: [
        {
          type: 'text',
          text: `# Deployment Configuration

\`\`\`yaml
${config}
\`\`\`

Save this as \`deployment-${args.app_type}.config.yml\` in your repository root.`,
        },
      ],
    };
  }

  generateConfig(args) {
    const {
      app_type,
      instance_name,
      aws_region = 'us-east-1',
      blueprint_id = 'ubuntu_22_04',
      bundle_id = 'small_3_0',
      enable_bucket = false,
      bucket_name,
      bucket_config = {},
      dependencies = [],
      database_type = 'none',
      use_rds = false,
    } = args;

    // Map blueprint_id to OS names for comments
    const osNames = {
      'ubuntu_22_04': 'Ubuntu 22.04 LTS',
      'ubuntu_20_04': 'Ubuntu 20.04 LTS', 
      'amazon_linux_2023': 'Amazon Linux 2023',
      'amazon_linux_2': 'Amazon Linux 2',
      'centos_7_2009_01': 'CentOS 7'
    };

    // Map bundle_id to size names for comments
    const sizeNames = {
      'nano_3_0': 'Nano (512MB)',
      'micro_3_0': 'Micro (1GB)',
      'small_3_0': 'Small (2GB)',
      'medium_3_0': 'Medium (4GB)',
      'large_3_0': 'Large (8GB)',
      'xlarge_3_0': 'XLarge (16GB)',
      '2xlarge_3_0': '2XLarge (32GB)'
    };

    let config = `# ${app_type.toUpperCase()} Deployment Configuration
aws:
  region: ${aws_region}

lightsail:
  instance_name: ${instance_name}
  static_ip: ""
  
  # Instance will be auto-created if it doesn't exist
  auto_create: true
  blueprint_id: "${blueprint_id}"  # ${osNames[blueprint_id] || blueprint_id}
  bundle_id: "${bundle_id}"  # ${sizeNames[bundle_id] || bundle_id}
`;

    if (enable_bucket && bucket_name) {
      config += `
  bucket:
    enabled: true
    name: ${bucket_name}
    access_level: ${bucket_config.access_level || 'read_write'}
    bundle_id: ${bucket_config.bundle_id || 'small_1_0'}
`;
    }

    config += `
application:
  name: ${instance_name}
  version: "1.0.0"
  type: ${app_type}
  package_fallback: true

dependencies:
`;

    // Add dependencies based on app type
    const depMap = {
      lamp: ['apache', 'php', 'mysql'],
      nginx: ['nginx'],
      nodejs: ['nodejs'],
      python: ['python', 'nginx'],
      react: ['nodejs', 'nginx'],
      docker: ['docker'],
    };

    const appDeps = depMap[app_type] || [];
    [...appDeps, ...dependencies].forEach((dep) => {
      config += `  ${dep}:
    enabled: true
`;
    });

    if (database_type !== 'none') {
      config += `  ${database_type}:
    enabled: true
    external: ${use_rds}
`;
    }

    config += `
deployment:
  use_docker: ${app_type === 'docker'}
  
monitoring:
  health_check:
    endpoint: "/"
    max_attempts: 10
`;

    return config;
  }

  async setupOIDC(args) {
    const { repo_owner, repo_name, role_name, trust_branch = 'main' } = args;

    const instructions = `# Set up GitHub Actions OIDC for AWS

Run these AWS CLI commands:

\`\`\`bash
# 1. Create OIDC provider (if doesn't exist)
aws iam create-open-id-connect-provider \\
  --url https://token.actions.githubusercontent.com \\
  --client-id-list sts.amazonaws.com \\
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# 2. Create IAM role
aws iam create-role \\
  --role-name ${role_name} \\
  --assume-role-policy-document '{
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
          "token.actions.githubusercontent.com:sub": "repo:${repo_owner}/${repo_name}:ref:refs/heads/${trust_branch}"
        }
      }
    }]
  }'

# 3. Attach policies
aws iam attach-role-policy \\
  --role-name ${role_name} \\
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# 4. Create custom Lightsail policy
aws iam create-policy \\
  --policy-name ${role_name}-LightsailAccess \\
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": "lightsail:*",
      "Resource": "*"
    }]
  }'

# 5. Attach custom policy
aws iam attach-role-policy \\
  --role-name ${role_name} \\
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/${role_name}-LightsailAccess

# 6. Get role ARN
aws iam get-role --role-name ${role_name} --query 'Role.Arn' --output text
\`\`\`

**Then set GitHub variable:**
\`\`\`bash
gh variable set AWS_ROLE_ARN --body "arn:aws:iam::ACCOUNT_ID:role/${role_name}"
\`\`\`

Replace ACCOUNT_ID with your AWS account ID.`;

    return {
      content: [{ type: 'text', text: instructions }],
    };
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
        status += `${emoji} **${run.name}** - ${run.status}\n`;
        status += `   ${run.url}\n\n`;
      });

      return {
        content: [{ type: 'text', text: status }],
      };
    } catch (error) {
      throw new Error('Failed to get deployment status. Make sure GitHub CLI is installed and authenticated.');
    }
  }

  async listExamples() {
    const examples = `# Available Example Applications

## 1. LAMP Stack
- Apache + PHP + MySQL/PostgreSQL
- Redis caching
- S3 bucket integration
- Perfect for: WordPress, Laravel, custom PHP apps

## 2. NGINX
- Static file serving
- Reverse proxy support
- SSL/TLS ready
- Perfect for: Static sites, SPAs, documentation

## 3. Node.js
- PM2 process manager
- NPM/Yarn support
- Database integration
- Perfect for: Express, Next.js, NestJS, APIs

## 4. Python
- Gunicorn WSGI server
- Virtual environment
- pip packages
- Perfect for: Flask, Django, FastAPI

## 5. React
- Production builds
- NGINX serving
- Environment variables
- Perfect for: CRA, Vite, Next.js static

## 6. Docker
- Multi-container architecture
- Docker Compose orchestration
- S3 bucket integration (optional)
- Perfect for: Complex apps, microservices

**All examples include:**
- Automatic deployment on push
- Health checks
- Monitoring
- S3 bucket support (optional)
- RDS database support (optional)`;

    return {
      content: [{ type: 'text', text: examples }],
    };
  }

  async diagnoseDeployment(args) {
    const { repo_path = '.', check_type = 'all' } = args;
    let report = '# Deployment Diagnostics Report\n\n';
    const issues = [];
    const warnings = [];
    const passed = [];

    // Check prerequisites
    if (check_type === 'all' || check_type === 'prerequisites') {
      report += '## Prerequisites Check\n\n';

      // Node.js
      try {
        const nodeVersion = execSync('node --version', { encoding: 'utf-8' }).trim();
        const majorVersion = parseInt(nodeVersion.replace('v', '').split('.')[0]);
        if (majorVersion >= 18) {
          passed.push(`Node.js ${nodeVersion}`);
          report += `✅ Node.js: ${nodeVersion}\n`;
        } else {
          issues.push(`Node.js version too old: ${nodeVersion} (need 18+)`);
          report += `❌ Node.js: ${nodeVersion} (need 18+)\n`;
        }
      } catch (error) {
        issues.push('Node.js not installed');
        report += '❌ Node.js: Not installed\n';
      }

      // GitHub CLI
      try {
        const ghVersion = execSync('gh --version', { encoding: 'utf-8' }).trim().split('\n')[0];
        passed.push('GitHub CLI');
        report += `✅ GitHub CLI: ${ghVersion}\n`;
      } catch (error) {
        issues.push('GitHub CLI not installed');
        report += '❌ GitHub CLI: Not installed\n';
        report += '   Install: brew install gh (macOS) or see https://cli.github.com\n';
      }

      // AWS CLI
      try {
        const awsVersion = execSync('aws --version', { encoding: 'utf-8' }).trim();
        passed.push('AWS CLI');
        report += `✅ AWS CLI: ${awsVersion}\n`;
      } catch (error) {
        warnings.push('AWS CLI not installed (needed for OIDC setup)');
        report += '⚠️  AWS CLI: Not installed (needed for OIDC setup)\n';
        report += '   Install: brew install awscli (macOS)\n';
      }

      // Git
      try {
        const gitVersion = execSync('git --version', { encoding: 'utf-8' }).trim();
        passed.push('Git');
        report += `✅ Git: ${gitVersion}\n`;
      } catch (error) {
        issues.push('Git not installed');
        report += '❌ Git: Not installed\n';
      }

      report += '\n';
    }

    // Check GitHub authentication
    if (check_type === 'all' || check_type === 'github') {
      report += '## GitHub Configuration\n\n';

      try {
        const ghAuth = execSync('gh auth status', { encoding: 'utf-8', stdio: 'pipe' });
        passed.push('GitHub authentication');
        report += '✅ GitHub CLI: Authenticated\n';
      } catch (error) {
        issues.push('GitHub CLI not authenticated');
        report += '❌ GitHub CLI: Not authenticated\n';
        report += '   Run: gh auth login\n';
      }

      // Check if in a git repo
      if (existsSync(join(repo_path, '.git'))) {
        passed.push('Git repository');
        report += '✅ Git repository: Found\n';

        try {
          const remote = execSync('git remote get-url origin', {
            cwd: repo_path,
            encoding: 'utf-8',
          }).trim();
          report += `   Remote: ${remote}\n`;
        } catch (error) {
          warnings.push('No git remote configured');
          report += '⚠️  No git remote configured\n';
        }
      } else {
        warnings.push('Not a git repository');
        report += '⚠️  Not a git repository\n';
      }

      report += '\n';
    }

    // Check AWS configuration
    if (check_type === 'all' || check_type === 'aws') {
      report += '## AWS Configuration\n\n';

      try {
        const identity = execSync('aws sts get-caller-identity', { encoding: 'utf-8' });
        const identityData = JSON.parse(identity);
        passed.push('AWS credentials');
        report += '✅ AWS Credentials: Configured\n';
        report += `   Account: ${identityData.Account}\n`;
        report += `   User: ${identityData.Arn}\n`;
      } catch (error) {
        warnings.push('AWS credentials not configured');
        report += '⚠️  AWS Credentials: Not configured\n';
        report += '   Run: aws configure\n';
      }

      // Check for OIDC provider
      try {
        const providers = execSync('aws iam list-open-id-connect-providers', { encoding: 'utf-8' });
        const providersData = JSON.parse(providers);
        const githubProvider = providersData.OpenIDConnectProviderList?.find((p) =>
          p.Arn.includes('token.actions.githubusercontent.com')
        );

        if (githubProvider) {
          passed.push('GitHub OIDC provider');
          report += '✅ GitHub OIDC Provider: Configured\n';
        } else {
          warnings.push('GitHub OIDC provider not found');
          report += '⚠️  GitHub OIDC Provider: Not found\n';
          report += '   Use setup_oidc_authentication tool to configure\n';
        }
      } catch (error) {
        // Ignore if can't check
      }

      report += '\n';
    }

    // Check deployment configuration
    if (check_type === 'all' || check_type === 'configuration') {
      report += '## Deployment Configuration\n\n';

      // Check for deployment config files
      const configFiles = ['lamp', 'nginx', 'nodejs', 'python', 'react', 'docker']
        .map((type) => `deployment-${type}.config.yml`)
        .filter((file) => existsSync(join(repo_path, file)));

      if (configFiles.length > 0) {
        passed.push('Deployment configuration');
        report += `✅ Deployment Config: Found ${configFiles.length} file(s)\n`;
        configFiles.forEach((file) => {
          report += `   - ${file}\n`;
        });
      } else {
        warnings.push('No deployment configuration files found');
        report += '⚠️  Deployment Config: No files found\n';
        report += '   Use generate_deployment_config tool to create\n';
      }

      // Check for workflows
      const workflowPath = join(repo_path, '.github/workflows');
      if (existsSync(workflowPath)) {
        passed.push('GitHub Actions workflows');
        report += '✅ GitHub Actions: Workflows found\n';
      } else {
        issues.push('No GitHub Actions workflows found');
        report += '❌ GitHub Actions: No workflows found\n';
        report += '   Use integrate_existing_repository tool to add\n';
      }

      // Check for Python deployment scripts
      const scriptsPath = join(repo_path, 'workflows');
      if (existsSync(scriptsPath)) {
        passed.push('Deployment scripts');
        report += '✅ Deployment Scripts: Found\n';
      } else {
        issues.push('No deployment scripts found');
        report += '❌ Deployment Scripts: Not found\n';
      }

      report += '\n';
    }

    // Check Lightsail instance
    if (check_type === 'all' || check_type === 'instance') {
      report += '## Lightsail Instance\n\n';

      // Try to get instance name from config
      let instanceName = null;
      for (const file of configFiles || []) {
        try {
          const configContent = execSync(`cat ${join(repo_path, file)}`, { encoding: 'utf-8' });
          const match = configContent.match(/instance_name:\s*(.+)/);
          if (match) {
            instanceName = match[1].trim();
            break;
          }
        } catch (error) {
          // Ignore
        }
      }

      if (instanceName) {
        report += `   Instance Name: ${instanceName}\n`;

        try {
          const instance = execSync(`aws lightsail get-instance --instance-name ${instanceName}`, {
            encoding: 'utf-8',
          });
          const instanceData = JSON.parse(instance);
          passed.push('Lightsail instance');
          report += `✅ Instance Status: ${instanceData.instance.state.name}\n`;
          report += `   IP: ${instanceData.instance.publicIpAddress}\n`;
          report += `   Region: ${instanceData.instance.location.regionName}\n`;
        } catch (error) {
          warnings.push(`Instance ${instanceName} not found or not accessible`);
          report += `⚠️  Instance: Not found or not accessible\n`;
        }
      } else {
        report += '⚠️  Instance Name: Not found in configuration\n';
      }

      report += '\n';
    }

    // Summary
    report += '## Summary\n\n';
    report += `✅ Passed: ${passed.length}\n`;
    report += `⚠️  Warnings: ${warnings.length}\n`;
    report += `❌ Issues: ${issues.length}\n\n`;

    if (issues.length > 0) {
      report += '### Critical Issues\n';
      issues.forEach((issue) => {
        report += `- ${issue}\n`;
      });
      report += '\n';
    }

    if (warnings.length > 0) {
      report += '### Warnings\n';
      warnings.forEach((warning) => {
        report += `- ${warning}\n`;
      });
      report += '\n';
    }

    // Recommendations
    report += '## Recommendations\n\n';

    if (issues.length === 0 && warnings.length === 0) {
      report += '✅ Everything looks good! Your deployment setup is ready.\n\n';
      report += '**Next Steps:**\n';
      report += '1. Commit and push your changes\n';
      report += '2. Monitor deployment with get_deployment_status\n';
      report += '3. Check application health after deployment\n';
    } else {
      report += 'Please address the issues and warnings above before deploying.\n\n';
      report += '**Quick Fixes:**\n';

      if (issues.some((i) => i.includes('GitHub CLI'))) {
        report += '- Install GitHub CLI: `brew install gh` (macOS)\n';
      }
      if (issues.some((i) => i.includes('authenticated'))) {
        report += '- Authenticate GitHub CLI: `gh auth login`\n';
      }
      if (issues.some((i) => i.includes('workflows'))) {
        report += '- Add workflows: Use integrate_existing_repository tool\n';
      }
      if (warnings.some((w) => w.includes('AWS'))) {
        report += '- Configure AWS: `aws configure`\n';
      }
      if (warnings.some((w) => w.includes('OIDC'))) {
        report += '- Set up OIDC: Use setup_oidc_authentication tool\n';
      }
    }

    report += '\n---\n\n';
    report += 'For detailed troubleshooting, see: [TROUBLESHOOTING.md](mcp-server/TROUBLESHOOTING.md)\n';

    return {
      content: [{ type: 'text', text: report }],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Lightsail Deployment MCP server running on stdio');
  }
}

const server = new LightsailDeploymentServer();
server.run().catch(console.error);
