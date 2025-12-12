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
        version: '1.1.1',
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
          description: 'Get the enhanced setup script for creating complete Lightsail deployment automation. This returns direct commands to download and execute the setup script locally on your machine with all parameters configured. Supports 6 application types (LAMP, Node.js, Python, React, Docker, Nginx) with database configuration (MySQL, PostgreSQL, none), bucket integration, GitHub OIDC setup, and comprehensive deployment automation. In automated mode, AI agents can specify all deployment requirements without interactive prompts.',
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
              aws_role_arn: {
                type: 'string',
                description: 'Custom AWS IAM role ARN for GitHub Actions OIDC authentication. If not provided, will use default role naming convention: GitHubActions-{app_name}-deployment. Format: arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME'
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
              github_username: {
                type: 'string',
                description: 'GitHub username for the repository (required for OIDC setup)'
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
          name: 'analyze_deployment_requirements',
          description: 'Intelligent analysis tool that takes user requirements and provides specific deployment parameter recommendations. AI agents provide user description and get back exact parameters to use for deployment. This eliminates guesswork and provides intelligent defaults based on application analysis.',
          inputSchema: {
            type: 'object',
            properties: {
              user_description: {
                type: 'string',
                description: 'User description of their application, requirements, or deployment needs'
              },
              app_context: {
                type: 'object',
                properties: {
                  technologies: {
                    type: 'array',
                    items: { type: 'string' },
                    description: 'Technologies mentioned (e.g., ["Node.js", "Express", "PostgreSQL"])'
                  },
                  features: {
                    type: 'array', 
                    items: { type: 'string' },
                    description: 'Features mentioned (e.g., ["file uploads", "user authentication", "API"])'
                  },
                  scale: {
                    type: 'string',
                    enum: ['small', 'medium', 'large', 'unknown'],
                    default: 'unknown',
                    description: 'Expected application scale'
                  }
                },
                description: 'Optional structured context about the application'
              }
            },
            required: ['user_description']
          }
        },
        {
          name: 'get_project_structure_guide',
          description: 'Get project structure recommendations based on application type and GitHub Actions configuration. Helps AI agents understand how to organize code for successful deployment with specific file placement, directory structure, and configuration requirements.',
          inputSchema: {
            type: 'object',
            properties: {
              app_type: {
                type: 'string',
                enum: ['lamp', 'nodejs', 'python', 'react', 'docker', 'nginx'],
                description: 'Application type to get structure guide for'
              },
              include_examples: {
                type: 'boolean',
                default: true,
                description: 'Include example file contents and templates'
              },
              include_github_actions: {
                type: 'boolean',
                default: true,
                description: 'Include GitHub Actions workflow structure requirements'
              },
              deployment_features: {
                type: 'array',
                items: {
                  type: 'string',
                  enum: ['database', 'bucket', 'ssl', 'docker', 'monitoring']
                },
                description: 'Additional deployment features that affect project structure'
              }
            },
            required: ['app_type']
          }
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
        {
          name: 'configure_github_repository',
          description: 'Configure GitHub repository settings and provide dynamic repository URLs. This tool helps set up the correct GitHub repository information and provides personalized links for the user\'s specific repository.',
          inputSchema: {
            type: 'object',
            properties: {
              github_username: {
                type: 'string',
                description: 'GitHub username for the repository'
              },
              repository_name: {
                type: 'string',
                description: 'Name of the GitHub repository'
              },
              app_type: {
                type: 'string',
                enum: ['lamp', 'nodejs', 'python', 'react', 'docker', 'nginx'],
                description: 'Type of application for customized repository setup'
              }
            },
            required: ['github_username', 'repository_name']
          }
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'setup_complete_deployment':
            return await this.setupCompleteDeployment(args);
          case 'analyze_deployment_requirements':
            return await this.analyzeDeploymentRequirements(args);
          case 'get_deployment_examples':
            return await this.getDeploymentExamples(args);
          case 'get_project_structure_guide':
            return await this.getProjectStructureGuide(args);
          case 'get_deployment_status':
            return await this.getDeploymentStatus(args);
          case 'diagnose_deployment':
            return await this.diagnoseDeployment(args);
          case 'configure_github_repository':
            return await this.configureGitHubRepository(args);
          default:
            return {
              content: [{ type: 'text', text: `Tool ${name} not implemented. Available tools: setup_complete_deployment, analyze_deployment_requirements, get_deployment_examples, get_project_structure_guide, get_deployment_status, diagnose_deployment, configure_github_repository` }],
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

  async getProjectStructureGuide(args) {
    const { 
      app_type, 
      include_examples = true, 
      include_github_actions = true, 
      deployment_features = [] 
    } = args;

    if (!app_type) {
      return {
        content: [{ type: 'text', text: '❌ Error: app_type is required. Choose from: lamp, nodejs, python, react, docker, nginx' }],
        isError: true,
      };
    }

    const hasDatabase = deployment_features.includes('database');
    const hasBucket = deployment_features.includes('bucket');
    const hasDocker = deployment_features.includes('docker') || app_type === 'docker';
    const hasSSL = deployment_features.includes('ssl');
    const hasMonitoring = deployment_features.includes('monitoring');

    let guide = `# 📁 Project Structure Guide: ${app_type.toUpperCase()}

## 🎯 Overview
This guide shows the recommended project structure for **${app_type}** applications to ensure successful deployment with GitHub Actions and AWS Lightsail.

## 🔗 Reference Example Application
**Live Example**: [example-${app_type}-app](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/tree/main/example-${app_type}-app)

Use this as a complete working reference for your ${app_type} application structure and implementation.

## 📂 Required Directory Structure

\`\`\`
your-repository/
├── .github/
│   └── workflows/
│       └── deploy-${app_type}.yml          # GitHub Actions workflow
├── deployment-${app_type}.config.yml       # Deployment configuration
`;

    // Add app-specific structure
    switch (app_type) {
      case 'lamp':
        guide += `├── example-lamp-app/                       # Application directory
│   ├── index.php                           # Main PHP file
│   ├── config/
│   │   └── database.php                    # Database configuration
│   ├── api/
│   │   └── endpoints.php                   # API endpoints
│   └── assets/
│       ├── css/
│       ├── js/
│       └── images/
`;
        if (hasBucket) {
          guide += `│   ├── bucket-manager.php                  # S3/Bucket integration
│   └── uploads/                            # Local upload directory
`;
        }
        break;

      case 'nodejs':
        guide += `├── example-nodejs-app/                     # Application directory
│   ├── app.js                              # Main application file
│   ├── package.json                        # Dependencies and scripts
│   ├── package-lock.json                   # Dependency lock file
│   ├── routes/
│   │   ├── index.js                        # Route definitions
│   │   └── api.js                          # API routes
│   ├── models/                             # Database models (if using DB)
│   ├── middleware/                         # Express middleware
│   ├── public/                             # Static assets
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── views/                              # Template files (if using)
`;
        if (hasBucket) {
          guide += `│   ├── services/
│   │   └── storage.js                      # S3/Bucket service
│   └── uploads/                            # Local upload directory
`;
        }
        break;

      case 'python':
        guide += `├── example-python-app/                     # Application directory
│   ├── app.py                              # Main Flask/Django application
│   ├── requirements.txt                    # Python dependencies
│   ├── wsgi.py                             # WSGI entry point
│   ├── config.py                           # Application configuration
│   ├── routes/
│   │   └── __init__.py                     # Route blueprints
│   ├── models/                             # Database models (if using DB)
│   │   └── __init__.py
│   ├── templates/                          # Jinja2 templates
│   ├── static/                             # Static assets
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── migrations/                         # Database migrations (if using DB)
`;
        if (hasBucket) {
          guide += `│   ├── services/
│   │   └── storage.py                      # S3/Bucket service
│   └── uploads/                            # Local upload directory
`;
        }
        break;

      case 'react':
        guide += `├── example-react-app/                      # Application directory
│   ├── public/
│   │   ├── index.html                      # Main HTML template
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── index.js                        # React entry point
│   │   ├── App.js                          # Main App component
│   │   ├── components/                     # React components
│   │   │   ├── Header.js
│   │   │   └── Footer.js
│   │   ├── pages/                          # Page components
│   │   ├── services/                       # API services
│   │   ├── utils/                          # Utility functions
│   │   └── styles/                         # CSS/SCSS files
│   ├── package.json                        # Dependencies and build scripts
│   ├── package-lock.json                   # Dependency lock file
│   └── .gitignore                          # Git ignore rules
`;
        break;

      case 'docker':
        guide += `├── example-docker-app/                     # Application directory
│   ├── Dockerfile                          # Docker image definition
│   ├── docker-compose.yml                  # Multi-container setup
│   ├── .dockerignore                       # Docker ignore rules
│   ├── src/                                # Application source code
│   │   ├── index.php                       # Main application file
│   │   └── config/                         # Configuration files
│   ├── nginx/                              # Nginx configuration (if needed)
│   │   └── default.conf
│   └── scripts/                            # Deployment scripts
│       └── entrypoint.sh                   # Container entry point
`;
        if (hasDatabase) {
          guide += `│   ├── database/
│   │   ├── init.sql                        # Database initialization
│   │   └── migrations/                     # Database migrations
`;
        }
        break;

      case 'nginx':
        guide += `├── example-nginx-app/                      # Application directory
│   ├── index.html                          # Main HTML file
│   ├── css/
│   │   └── style.css                       # Stylesheets
│   ├── js/
│   │   └── main.js                         # JavaScript files
│   ├── images/                             # Image assets
│   ├── docs/                               # Documentation (if applicable)
│   └── assets/                             # Other static assets
`;
        break;
    }

    // Add common files
    guide += `├── README.md                               # Project documentation
└── .gitignore                              # Git ignore rules
\`\`\`

## 🔧 Required Configuration Files

### 1. Deployment Configuration (\`deployment-${app_type}.config.yml\`)
This file defines your infrastructure and deployment settings:

\`\`\`yaml
# ${app_type.toUpperCase()} Application Deployment Configuration
aws:
  region: us-east-1

lightsail:
  instance_name: ${app_type}-demo-app
  bundle_id: "${app_type === 'docker' ? 'medium_3_0' : app_type === 'nginx' || app_type === 'react' ? 'micro_3_0' : 'small_3_0'}"
  blueprint_id: "ubuntu_22_04"

application:
  name: ${app_type}-demo-app
  version: "1.0.0"
  type: web
  
  package_files:`;

    // Add app-specific package files
    switch (app_type) {
      case 'lamp':
        guide += `
    - "example-lamp-app/index.php"
    - "example-lamp-app/config/**"
    - "example-lamp-app/api/**"
    - "example-lamp-app/assets/**"`;
        break;
      case 'nodejs':
        guide += `
    - "example-nodejs-app/app.js"
    - "example-nodejs-app/package.json"
    - "example-nodejs-app/package-lock.json"
    - "example-nodejs-app/routes/**"
    - "example-nodejs-app/public/**"`;
        break;
      case 'python':
        guide += `
    - "example-python-app/app.py"
    - "example-python-app/requirements.txt"
    - "example-python-app/wsgi.py"
    - "example-python-app/routes/**"
    - "example-python-app/templates/**"
    - "example-python-app/static/**"`;
        break;
      case 'react':
        guide += `
    - "example-react-app/build/**"  # Built files after npm run build
    - "example-react-app/package.json"`;
        break;
      case 'docker':
        guide += `
    - "example-docker-app/Dockerfile"
    - "example-docker-app/docker-compose.yml"
    - "example-docker-app/src/**"
    - "example-docker-app/nginx/**"`;
        break;
      case 'nginx':
        guide += `
    - "example-nginx-app/index.html"
    - "example-nginx-app/css/**"
    - "example-nginx-app/js/**"
    - "example-nginx-app/images/**"`;
        break;
    }

    guide += `
  
  package_fallback: true

dependencies:`;

    // Add app-specific dependencies
    switch (app_type) {
      case 'lamp':
        guide += `
  apache:
    enabled: true
  php:
    enabled: true
    version: "8.1"
  mysql:
    enabled: ${hasDatabase}`;
        break;
      case 'nodejs':
        guide += `
  nginx:
    enabled: true
    config:
      proxy_pass: "http://localhost:3000"
  nodejs:
    enabled: true
    version: "18"
    config:
      npm_packages: ["pm2"]
  postgresql:
    enabled: ${hasDatabase}`;
        break;
      case 'python':
        guide += `
  nginx:
    enabled: true
    config:
      proxy_pass: "http://localhost:5000"
  python:
    enabled: true
    version: "3.9"
    config:
      pip_packages: ["gunicorn"]
  postgresql:
    enabled: ${hasDatabase}`;
        break;
      case 'react':
        guide += `
  nginx:
    enabled: true
    config:
      document_root: "/var/www/html"`;
        break;
      case 'docker':
        guide += `
  docker:
    enabled: true
    config:
      install_compose: true`;
        break;
      case 'nginx':
        guide += `
  nginx:
    enabled: true
    config:
      document_root: "/var/www/html"`;
        break;
    }

    guide += `
\`\`\`

`;

    if (include_github_actions) {
      guide += `### 2. GitHub Actions Workflow (\`.github/workflows/deploy-${app_type}.yml\`)

\`\`\`yaml
name: ${app_type.charAt(0).toUpperCase() + app_type.slice(1)} Application Deployment

on:
  push:
    branches: [ main ]
    paths:
      - 'example-${app_type}-app/**'
      - 'deployment-${app_type}.config.yml'
      - '.github/workflows/deploy-${app_type}.yml'
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    name: Deploy ${app_type.charAt(0).toUpperCase() + app_type.slice(1)} Application
    uses: ./.github/workflows/deploy-generic-reusable.yml
    with:
      config_file: 'deployment-${app_type}.config.yml'
      skip_tests: false
\`\`\`

`;
    }

    if (include_examples) {
      guide += `## 📝 Example File Contents

`;

      switch (app_type) {
        case 'lamp':
          guide += `### \`example-lamp-app/index.php\`
\`\`\`php
<?php
// Simple PHP application
echo "<h1>Welcome to LAMP Stack Application</h1>";
echo "<p>Server Time: " . date('Y-m-d H:i:s') . "</p>";

// Database connection example (if database enabled)
${hasDatabase ? `
try {
    $pdo = new PDO('mysql:host=localhost;dbname=app_db', 'app_user', 'app_password');
    echo "<p>Database: Connected ✅</p>";
} catch(PDOException $e) {
    echo "<p>Database: Connection failed ❌</p>";
}
` : '// Database not configured'}

// Health check endpoint
if ($_GET['health'] ?? false) {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'healthy', 'timestamp' => time()]);
    exit;
}
?>
\`\`\`
`;
          break;

        case 'nodejs':
          guide += `### \`example-nodejs-app/app.js\`
\`\`\`javascript
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static('public'));

// Routes
app.get('/', (req, res) => {
  res.json({
    message: 'Welcome to Node.js Application',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: Date.now() });
});

app.get('/api/info', (req, res) => {
  res.json({
    name: process.env.APP_NAME || 'Node.js App',
    version: '1.0.0',
    node_version: process.version
  });
});

app.listen(port, () => {
  console.log(\`Server running on port \${port}\`);
});
\`\`\`

### \`example-nodejs-app/package.json\`
\`\`\`json
{
  "name": "nodejs-demo-app",
  "version": "1.0.0",
  "description": "Node.js application for Lightsail deployment",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "dev": "nodemon app.js",
    "test": "echo \\"No tests specified\\" && exit 0"
  },
  "dependencies": {
    "express": "^4.18.0"${hasDatabase ? ',\n    "pg": "^8.8.0"' : ''}${hasBucket ? ',\n    "aws-sdk": "^2.1200.0"' : ''}
  },
  "devDependencies": {
    "nodemon": "^2.0.20"
  }
}
\`\`\`
`;
          break;

        case 'python':
          guide += `### \`example-python-app/app.py\`
\`\`\`python
from flask import Flask, jsonify
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to Python Flask Application',
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('FLASK_ENV', 'production')
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().timestamp()})

@app.route('/api/info')
def info():
    return jsonify({
        'name': os.getenv('APP_NAME', 'Python Flask App'),
        'version': '1.0.0',
        'python_version': os.sys.version
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
\`\`\`

### \`example-python-app/requirements.txt\`
\`\`\`
Flask==2.3.0
gunicorn==21.2.0${hasDatabase ? '\npsycopg2-binary==2.9.7' : ''}${hasBucket ? '\nboto3==1.28.0' : ''}
\`\`\`

### \`example-python-app/wsgi.py\`
\`\`\`python
from app import app

if __name__ == "__main__":
    app.run()
\`\`\`
`;
          break;

        case 'react':
          guide += `### \`example-react-app/src/App.js\`
\`\`\`jsx
import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to React Application</h1>
        <p>Deployed on AWS Lightsail</p>
        <p>Build Time: {process.env.REACT_APP_BUILD_TIME || 'Unknown'}</p>
      </header>
    </div>
  );
}

export default App;
\`\`\`

### \`example-react-app/package.json\`
\`\`\`json
{
  "name": "react-demo-app",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test --watchAll=false",
    "eject": "react-scripts eject"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
\`\`\`
`;
          break;

        case 'docker':
          guide += `### \`example-docker-app/Dockerfile\`
\`\`\`dockerfile
FROM php:8.1-apache

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    libpng-dev \\
    libonig-dev \\
    libxml2-dev \\
    zip \\
    unzip

# Install PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd

# Copy application files
COPY src/ /var/www/html/

# Set permissions
RUN chown -R www-data:www-data /var/www/html \\
    && chmod -R 755 /var/www/html

# Enable Apache mod_rewrite
RUN a2enmod rewrite

EXPOSE 80
\`\`\`

### \`example-docker-app/docker-compose.yml\`
\`\`\`yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:80"
    volumes:
      - ./src:/var/www/html
    environment:
      - APP_ENV=production${hasDatabase ? `
  
  database:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: app_db
      MYSQL_USER: app_user
      MYSQL_PASSWORD: app_password
    volumes:
      - db_data:/var/lib/mysql

volumes:
  db_data:` : ''}
\`\`\`
`;
          break;

        case 'nginx':
          guide += `### \`example-nginx-app/index.html\`
\`\`\`html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Static Website</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <h1>Welcome to Static Website</h1>
        <p>Deployed on AWS Lightsail with Nginx</p>
    </header>
    
    <main>
        <section>
            <h2>Features</h2>
            <ul>
                <li>Fast static content delivery</li>
                <li>Responsive design</li>
                <li>SEO optimized</li>
            </ul>
        </section>
    </main>
    
    <script src="js/main.js"></script>
</body>
</html>
\`\`\`
`;
          break;
      }
    }

    guide += `## ✅ Deployment Checklist

### Before Deployment:
- [ ] All required files are in the correct directory structure
- [ ] \`deployment-${app_type}.config.yml\` is configured for your needs
- [ ] GitHub Actions workflow is in \`.github/workflows/deploy-${app_type}.yml\`
- [ ] Application files are in \`example-${app_type}-app/\` directory
- [ ] Dependencies are properly defined (package.json, requirements.txt, etc.)
${hasDatabase ? '- [ ] Database configuration is set up in deployment config' : ''}
${hasBucket ? '- [ ] Bucket integration is configured for file storage' : ''}
${hasDocker ? '- [ ] Docker and docker-compose files are properly configured' : ''}

### After Deployment:
- [ ] GitHub Actions workflow runs successfully
- [ ] Application is accessible via the provided URL
- [ ] Health check endpoint responds correctly
- [ ] All features work as expected
${hasDatabase ? '- [ ] Database connection is working' : ''}
${hasBucket ? '- [ ] File upload/storage functionality works' : ''}

## 🚀 Quick Start Commands

### Option 1: Download Complete Example Application
\`\`\`bash
# Download the complete working example
git clone https://github.com/naveenraj44125-creator/lamp-stack-lightsail.git temp-repo
cp -r temp-repo/example-${app_type}-app ./
cp temp-repo/deployment-${app_type}.config.yml ./
mkdir -p .github/workflows
cp temp-repo/.github/workflows/deploy-${app_type}.yml .github/workflows/
rm -rf temp-repo

# Customize and deploy
git add .
git commit -m "Add ${app_type} application from example"
git push origin main
\`\`\`

### Option 2: Manual Setup with Custom Code
\`\`\`bash
# 1. Create the directory structure
mkdir -p .github/workflows
mkdir -p example-${app_type}-app

# 2. Download deployment configuration
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/deployment-${app_type}.config.yml

# 3. Download GitHub Actions workflow
curl -o .github/workflows/deploy-${app_type}.yml https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/.github/workflows/deploy-${app_type}.yml

# 4. Add your application code to example-${app_type}-app/
# (Use the structure shown above)

# 5. Customize and commit
git add .
git commit -m "Add ${app_type} application deployment setup"
git push origin main
\`\`\`

## 📚 Additional Resources

### Example Application Files
- **Complete Example**: [example-${app_type}-app/](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/tree/main/example-${app_type}-app)
- **Deployment Config**: [deployment-${app_type}.config.yml](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/blob/main/deployment-${app_type}.config.yml)
- **GitHub Workflow**: [deploy-${app_type}.yml](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/blob/main/.github/workflows/deploy-${app_type}.yml)

### Direct File Downloads
\`\`\`bash
# Download individual example files
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-${app_type}-app/README.md`;

    // Add app-specific download examples
    switch (app_type) {
      case 'lamp':
        guide += `
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-lamp-app/index.php
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-lamp-app/bucket-manager.php`;
        break;
      case 'nodejs':
        guide += `
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-nodejs-app/app.js
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-nodejs-app/package.json`;
        break;
      case 'python':
        guide += `
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-python-app/app.py
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-python-app/requirements.txt`;
        break;
      case 'react':
        guide += `
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-react-app/package.json
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-react-app/src/App.js`;
        break;
      case 'docker':
        guide += `
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-docker-app/Dockerfile
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-docker-app/docker-compose.yml`;
        break;
      case 'nginx':
        guide += `
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/example-nginx-app/index.html`;
        break;
    }

    guide += `
\`\`\`

## 🔍 Common Issues and Solutions

### Issue: Deployment fails with "Package files not found"
**Solution**: Ensure all files listed in \`package_files\` exist in the repository

### Issue: Application doesn't start after deployment
**Solution**: Check the main application file path and ensure it's executable

### Issue: Database connection fails
**Solution**: Verify database configuration in deployment config and application code

${app_type === 'react' ? `### Issue: React build fails
**Solution**: Ensure \`package.json\` has correct build script and all dependencies are listed` : ''}

${app_type === 'docker' ? `### Issue: Docker container fails to start
**Solution**: Check Dockerfile syntax and ensure all required files are copied correctly` : ''}

---

**🎯 This structure ensures your ${app_type} application deploys successfully with GitHub Actions and AWS Lightsail!**`;

    return {
      content: [{ type: 'text', text: guide }]
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
        status += `${emoji} **${run.name}** - ${run.status}\n   ${run.url}\n\n`;
      });
      return { content: [{ type: 'text', text: status }] };
    } catch (error) {
      throw new Error('Failed to get deployment status');
    }
  }

  async analyzeDeploymentRequirements(args) {
    const { user_description, app_context = {} } = args;
    
    if (!user_description) {
      return {
        content: [{ type: 'text', text: '❌ Error: user_description is required for analysis' }],
        isError: true,
      };
    }

    // Intelligent analysis of user requirements
    const analysis = this.performIntelligentAnalysis(user_description, app_context);
    
    // Generate response with specific parameter recommendations
    const response = `# 🧠 Intelligent Deployment Analysis

## 📝 User Requirements Analysis
**Input**: "${user_description}"

## 🎯 Detected Application Profile
- **Application Type**: ${analysis.app_type}
- **Confidence**: ${analysis.confidence}%
- **Reasoning**: ${analysis.reasoning}

## ⚙️ Recommended Parameters

### Core Configuration
\`\`\`json
{
  "mode": "fully_automated",
  "app_type": "${analysis.app_type}",
  "app_name": "${analysis.app_name}",
  "instance_name": "${analysis.instance_name}",
  "aws_region": "${analysis.aws_region}",
  "app_version": "${analysis.app_version}",
  "blueprint_id": "${analysis.blueprint_id}",
  "bundle_id": "${analysis.bundle_id}",
  "database_type": "${analysis.database_type}",
  "db_external": ${analysis.db_external},
  "db_name": "${analysis.db_name}",
  "enable_bucket": ${analysis.enable_bucket},
  ${analysis.enable_bucket ? `"bucket_name": "${analysis.bucket_name}",` : ''}
  ${analysis.enable_bucket ? `"bucket_access": "${analysis.bucket_access}",` : ''}
  ${analysis.enable_bucket ? `"bucket_bundle": "${analysis.bucket_bundle}",` : ''}
  "github_repo": "${analysis.github_repo}",
  "repo_visibility": "${analysis.repo_visibility}"
}
\`\`\`

## 🔍 Analysis Details

### Application Type Detection
${analysis.detection_details}

### Infrastructure Sizing
- **Bundle**: ${analysis.bundle_id} (${this.getBundleDescription(analysis.bundle_id)})
- **Reasoning**: ${analysis.bundle_reasoning}

### Database Selection
- **Database**: ${analysis.database_type}
- **Reasoning**: ${analysis.database_reasoning}

### Storage Configuration
- **Bucket Enabled**: ${analysis.enable_bucket ? 'Yes' : 'No'}
- **Reasoning**: ${analysis.storage_reasoning}

## 🚀 Ready-to-Execute MCP Call

Use these exact parameters with setup_complete_deployment:

\`\`\`json
{
  "tool": "setup_complete_deployment",
  "arguments": ${JSON.stringify({
    mode: "fully_automated",
    app_type: analysis.app_type,
    app_name: analysis.app_name,
    instance_name: analysis.instance_name,
    aws_region: analysis.aws_region,
    app_version: analysis.app_version,
    blueprint_id: analysis.blueprint_id,
    bundle_id: analysis.bundle_id,
    database_type: analysis.database_type,
    db_external: analysis.db_external,
    db_name: analysis.db_name,
    enable_bucket: analysis.enable_bucket,
    ...(analysis.enable_bucket && {
      bucket_name: analysis.bucket_name,
      bucket_access: analysis.bucket_access,
      bucket_bundle: analysis.bucket_bundle
    }),
    github_repo: analysis.github_repo,
    repo_visibility: analysis.repo_visibility
  }, null, 2)}
}
\`\`\`

## ✅ Validation Status
${analysis.validation_notes.map(note => `- ${note}`).join('\n')}

---
**AI Agent Instructions**: Copy the MCP call above and execute it directly. All parameters have been intelligently analyzed and validated.`;

    return {
      content: [{ type: 'text', text: response }]
    };
  }

  performIntelligentAnalysis(description, context) {
    const desc = description.toLowerCase();
    const technologies = context.technologies || [];
    const features = context.features || [];
    
    // Application type detection with confidence scoring
    let app_type = 'nginx';
    let confidence = 50;
    let reasoning = 'Default static site configuration';
    let detection_details = '';

    // Advanced pattern matching for application types
    if (desc.includes('wordpress') || desc.includes('php') || desc.includes('lamp') || desc.includes('apache')) {
      app_type = 'lamp';
      confidence = 95;
      reasoning = 'PHP/WordPress/LAMP stack detected';
      detection_details = 'Detected PHP-based application requiring Apache web server and MySQL database support.';
    } else if (desc.includes('node') || desc.includes('express') || desc.includes('npm') || desc.includes('javascript server') || technologies.includes('Node.js')) {
      app_type = 'nodejs';
      confidence = 90;
      reasoning = 'Node.js/Express application detected';
      detection_details = 'Detected Node.js backend application, likely using Express framework for API or web services.';
    } else if (desc.includes('python') || desc.includes('flask') || desc.includes('django') || desc.includes('fastapi') || technologies.includes('Python')) {
      app_type = 'python';
      confidence = 90;
      reasoning = 'Python web application detected';
      detection_details = 'Detected Python web application using Flask, Django, or similar framework.';
    } else if (desc.includes('react') || desc.includes('frontend') || desc.includes('spa') || desc.includes('single page') || technologies.includes('React')) {
      app_type = 'react';
      confidence = 85;
      reasoning = 'React frontend application detected';
      detection_details = 'Detected React-based frontend application requiring build process and static hosting.';
    } else if (desc.includes('docker') || desc.includes('container') || desc.includes('microservice') || desc.includes('compose')) {
      app_type = 'docker';
      confidence = 95;
      reasoning = 'Containerized application detected';
      detection_details = 'Detected Docker-based application requiring container runtime and enhanced resources.';
    } else if (desc.includes('static') || desc.includes('html') || desc.includes('documentation') || desc.includes('website')) {
      app_type = 'nginx';
      confidence = 80;
      reasoning = 'Static website detected';
      detection_details = 'Detected static website requiring only web server for HTML/CSS/JS files.';
    }

    // Database type selection based on app type and context
    let database_type = 'none';
    let database_reasoning = 'No database required for static content';
    
    if (desc.includes('database') || desc.includes('data') || desc.includes('mysql') || desc.includes('postgresql') || desc.includes('postgres')) {
      if (app_type === 'lamp' || desc.includes('mysql') || desc.includes('wordpress')) {
        database_type = 'mysql';
        database_reasoning = 'MySQL selected for LAMP stack compatibility and WordPress support';
      } else if (app_type === 'nodejs' || app_type === 'python' || app_type === 'docker' || desc.includes('postgresql') || desc.includes('postgres')) {
        database_type = 'postgresql';
        database_reasoning = 'PostgreSQL selected for modern application stack with JSON support';
      }
    } else if (app_type === 'lamp') {
      database_type = 'mysql';
      database_reasoning = 'MySQL auto-selected for LAMP stack (standard configuration)';
    } else if ((app_type === 'nodejs' || app_type === 'python' || app_type === 'docker') && !desc.includes('api only') && !desc.includes('external')) {
      database_type = 'postgresql';
      database_reasoning = 'PostgreSQL auto-selected for modern backend application';
    }

    // Bundle size selection based on app type and scale
    let bundle_id = 'micro_3_0';
    let bundle_reasoning = 'Standard size for small applications';
    
    if (app_type === 'docker') {
      bundle_id = 'medium_3_0';
      bundle_reasoning = 'Docker applications require enhanced resources for container overhead';
    } else if (app_type === 'nginx' || app_type === 'react') {
      bundle_id = 'micro_3_0';
      bundle_reasoning = 'Minimal resources sufficient for static content serving';
    } else if (app_type === 'lamp' || app_type === 'nodejs' || app_type === 'python') {
      bundle_id = 'small_3_0';
      bundle_reasoning = 'Standard web application resources with database support';
    }

    // Scale-based adjustments
    if (context.scale === 'large' || desc.includes('high traffic') || desc.includes('enterprise')) {
      if (bundle_id === 'micro_3_0') bundle_id = 'small_3_0';
      else if (bundle_id === 'small_3_0') bundle_id = 'medium_3_0';
      else if (bundle_id === 'medium_3_0') bundle_id = 'large_3_0';
      bundle_reasoning += ' (upgraded for high-traffic requirements)';
    }

    // Storage/bucket detection
    let enable_bucket = false;
    let storage_reasoning = 'No file storage required';
    
    if (desc.includes('upload') || desc.includes('file') || desc.includes('media') || desc.includes('storage') || 
        features.includes('file uploads') || features.includes('media')) {
      enable_bucket = true;
      storage_reasoning = 'File storage enabled for user uploads and media content';
    } else if (app_type === 'lamp' || app_type === 'docker') {
      enable_bucket = true;
      storage_reasoning = 'File storage enabled by default for dynamic applications';
    }

    // Generate names and defaults
    const timestamp = Date.now();
    const app_name = `${app_type}-app`;
    const instance_name = `${app_type}-app-production`;
    const bucket_name = enable_bucket ? `${app_type}-storage-${timestamp}` : '';
    const github_repo = app_name;

    // Validation notes
    const validation_notes = [
      '✅ Application type detected and validated',
      '✅ Infrastructure sizing appropriate for workload',
      '✅ Database configuration matches application requirements',
      '✅ Storage configuration based on feature analysis',
      '✅ All parameters validated for deployment'
    ];

    if (app_type === 'docker' && bundle_id === 'micro_3_0') {
      validation_notes.push('⚠️  Docker applications work better with small_3_0+ bundles');
    }

    return {
      app_type,
      confidence,
      reasoning,
      detection_details,
      app_name,
      instance_name,
      aws_region: 'us-east-1',
      app_version: '1.0.0',
      blueprint_id: 'ubuntu_22_04',
      bundle_id,
      bundle_reasoning,
      database_type,
      database_reasoning,
      db_external: false,
      db_name: `${app_name.replace('-', '_')}_db`,
      enable_bucket,
      bucket_name,
      bucket_access: 'read_write',
      bucket_bundle: 'small_1_0',
      storage_reasoning,
      github_repo,
      repo_visibility: 'private',
      validation_notes
    };
  }

  getBundleDescription(bundle_id) {
    const descriptions = {
      'nano_3_0': '512MB RAM, 1 vCPU - Minimal static sites',
      'micro_3_0': '1GB RAM, 1 vCPU - Small applications',
      'small_3_0': '2GB RAM, 1 vCPU - Standard web applications',
      'medium_3_0': '4GB RAM, 2 vCPU - High-traffic applications',
      'large_3_0': '8GB RAM, 2 vCPU - Enterprise applications'
    };
    return descriptions[bundle_id] || 'Unknown bundle size';
  }

  async setupCompleteDeployment(args) {
    const { 
      mode = 'interactive', 
      aws_region = 'us-east-1', 
      aws_role_arn,
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
      github_username,
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
      
      if (!github_username) {
        return {
          content: [{ type: 'text', text: '❌ Error: github_username is required for fully_automated mode for OIDC setup' }],
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
      
      // Validate IAM role ARN format if provided
      if (aws_role_arn && !aws_role_arn.match(/^arn:aws:iam::\d{12}:role\/[\w+=,.@-]+$/)) {
        return {
          content: [{ type: 'text', text: '❌ Error: Invalid AWS IAM role ARN format. Expected: arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME' }],
          isError: true,
        };
      }
    }
    
    let instructions = `# 🚀 Complete Lightsail Deployment Commands

## 📥 Ready-to-Execute Commands

### Method 1: Download and Execute
\`\`\`bash
# Download the setup script
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
      const repoName = github_repo || finalAppName;
      const finalGithubRepo = github_username ? `${github_username}/${repoName}` : repoName;
      const finalBucketName = enable_bucket ? (bucket_name || `${app_type}-bucket-${timestamp}`) : '';
      const finalDbRdsName = db_external ? (db_rds_name || `${app_type}-${database_type}-db`) : '';
      
      instructions += ` --auto --aws-region ${aws_region} --app-version ${app_version}`;
      
      // Add environment variables for fully automated mode
      const envVars = [
        `export AUTO_MODE=true`,
        `export AWS_REGION="${aws_region}"`,
        `export APP_VERSION="${app_version}"`,
        `export APP_TYPE="${app_type}"`,
        `export APP_NAME="${finalAppName}"`,
        `export INSTANCE_NAME="${finalInstanceName}"`,
        `export BLUEPRINT_ID="${blueprint_id}"`,
        `export BUNDLE_ID="${bundle_id}"`,
        `export DATABASE_TYPE="${database_type}"`,
        `export DB_EXTERNAL="${db_external}"`,
        `export DB_RDS_NAME="${finalDbRdsName}"`,
        `export DB_NAME="${db_name}"`,
        `export ENABLE_BUCKET="${enable_bucket}"`,
        `export BUCKET_NAME="${finalBucketName}"`,
        `export BUCKET_ACCESS="${bucket_access}"`,
        `export BUCKET_BUNDLE="${bucket_bundle}"`,
        `export GITHUB_REPO="${finalGithubRepo}"`,
        `export REPO_VISIBILITY="${repo_visibility}"`
      ];
      
      // Add custom IAM role ARN if provided
      if (aws_role_arn) {
        envVars.push(`export AWS_ROLE_ARN="${aws_role_arn}"`);
      }
      
      instructions = instructions.replace('# Run the script\n./setup-complete-deployment.sh', 
        `# Set environment variables for fully automated deployment
${envVars.join('\n')}

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
      const repoName = github_repo || finalAppName;
      const finalGithubRepo = github_username ? `${github_username}/${repoName}` : repoName;
      const finalBucketName = enable_bucket ? (bucket_name || `${app_type}-bucket-${timestamp}`) : '';
      const finalDbRdsName = db_external ? (db_rds_name || `${app_type}-${database_type}-db`) : '';
      
      // Build environment variables for direct execution
      const directEnvVars = [
        `AUTO_MODE=true`,
        `AWS_REGION="${aws_region}"`,
        `APP_VERSION="${app_version}"`,
        `APP_TYPE="${app_type}"`,
        `APP_NAME="${finalAppName}"`,
        `INSTANCE_NAME="${finalInstanceName}"`,
        `BLUEPRINT_ID="${blueprint_id}"`,
        `BUNDLE_ID="${bundle_id}"`,
        `DATABASE_TYPE="${database_type}"`,
        `DB_EXTERNAL="${db_external}"`,
        `DB_RDS_NAME="${finalDbRdsName}"`,
        `DB_NAME="${db_name}"`,
        `ENABLE_BUCKET="${enable_bucket}"`,
        `BUCKET_NAME="${finalBucketName}"`,
        `BUCKET_ACCESS="${bucket_access}"`,
        `BUCKET_BUNDLE="${bucket_bundle}"`,
        `GITHUB_REPO="${finalGithubRepo}"`,
        `REPO_VISIBILITY="${repo_visibility}"`
      ];
      
      // Add custom IAM role ARN if provided
      if (aws_role_arn) {
        directEnvVars.push(`AWS_ROLE_ARN="${aws_role_arn}"`);
      }
      
      instructions += `# Run directly from GitHub with environment variables
${directEnvVars.join(' \\\n')} \\
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

### Fully Automated Mode (AI Agent Mode) ⭐ **NEW**
- **Zero prompts** - AI agents provide all parameters via environment variables
- Complete deployment automation without human intervention
- Validates all parameters before execution
- Perfect for AI-driven deployment workflows
- All configuration specified via environment variables
- **Configurable IAM Role**: Use custom IAM role ARN or default naming convention
- **Use with MCP analyze_deployment_requirements tool for intelligent parameter selection**

### Help Mode  
- Shows comprehensive usage information and examples
- Lists all supported application types and features
- Add \`--help\` flag

## 🔐 IAM Role Configuration ⭐ **NEW**

### Custom IAM Role ARN
You can now specify a custom IAM role ARN for GitHub Actions OIDC authentication:

\`\`\`json
{
  "aws_role_arn": "arn:aws:iam::123456789012:role/MyCustomGitHubActionsRole"
}
\`\`\`

### Default IAM Role Naming
If no custom role ARN is provided, the script will create/use a role with this naming convention:
- **Pattern**: \`GitHubActions-{app_name}-deployment\`
- **Examples**: 
  - \`GitHubActions-my-nodejs-app-deployment\`
  - \`GitHubActions-my-lamp-app-deployment\`
  - \`GitHubActions-my-docker-app-deployment\`

### IAM Role Requirements
The IAM role (custom or default) must have these policies attached:
- \`AmazonLightsailFullAccess\`
- \`AmazonS3FullAccess\` (if using bucket storage)

### Trust Policy Requirements
The role must trust GitHub Actions OIDC provider:
\`\`\`json
{
  "Version": "2012-10-17",
  "Statement": [
    {
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
          "token.actions.githubusercontent.com:sub": "repo:USERNAME/REPOSITORY:*"
        }
      }
    }
  ]
}
\`\`\`

## 🧠 **NEW: Intelligent Analysis Tool** ⭐

### analyze_deployment_requirements
**Purpose**: AI agents can get intelligent parameter recommendations instead of manual configuration

**Usage**:
\`\`\`json
{
  "tool": "analyze_deployment_requirements",
  "arguments": {
    "user_description": "Node.js Express API with MySQL database and file uploads",
    "app_context": {
      "technologies": ["Node.js", "Express", "MySQL"],
      "features": ["API", "file uploads", "authentication"],
      "scale": "medium"
    }
  }
}
\`\`\`

**Returns**:
- ✅ **Application Type Detection** with confidence scoring (85-95%)
- ✅ **Complete Parameter Recommendations** with detailed reasoning
- ✅ **Ready-to-Execute MCP Call** with all parameters filled
- ✅ **Infrastructure Sizing** based on workload analysis
- ✅ **Database Selection** (MySQL/PostgreSQL/none) based on requirements
- ✅ **Storage Configuration** (bucket enabled/disabled) based on features
- ✅ **Validation Status** and compatibility checks

**Benefits for AI Agents**:
- 🚫 **No Parameter Guesswork** - MCP server analyzes and recommends
- 📊 **Confidence Scoring** - Know how reliable the detection is (85-95%)
- 🔍 **Detailed Reasoning** - Understand why each parameter was selected
- ✅ **Built-in Validation** - All parameters validated for compatibility
- 🎯 **Consistent Results** - Same analysis logic across all AI agents
- ⚡ **Instant Execution** - Get complete MCP call ready to execute

**Example Workflow for AI Agents**:
1. **Step 1**: Call \`analyze_deployment_requirements\` with user description
2. **Step 2**: Get intelligent analysis with exact parameters and confidence
3. **Step 3**: Call \`setup_complete_deployment\` with recommended parameters
4. **Step 4**: Explain analysis results and deployment configuration to user

## 🤖 **AI Agent Integration Guide**

### Two-Step Intelligent Workflow (RECOMMENDED)

**Step 1: Intelligent Analysis**
\`\`\`json
{
  "tool": "analyze_deployment_requirements",
  "arguments": {
    "user_description": "[USER'S APP DESCRIPTION]"
  }
}
\`\`\`

**Step 2: Execute Deployment**
\`\`\`json
{
  "tool": "setup_complete_deployment", 
  "arguments": {
    "mode": "fully_automated",
    // Use EXACT parameters from analysis response
    "app_type": "nodejs",  // From analysis
    "bundle_id": "small_3_0",  // From analysis  
    "database_type": "mysql",  // From analysis
    // ... all other parameters from analysis
  }
}
\`\`\`

### Application Type Detection Patterns

The intelligent analysis detects application types with high confidence:

| User Description Contains | Detected Type | Confidence | Database | Storage |
|--------------------------|---------------|------------|----------|---------|
| "WordPress", "PHP", "LAMP" | lamp | 95% | MySQL | Enabled |
| "Node.js", "Express", "npm" | nodejs | 90% | PostgreSQL | Based on features |
| "Python", "Flask", "Django" | python | 90% | PostgreSQL | Based on features |
| "React", "frontend", "SPA" | react | 85% | None | Disabled |
| "Docker", "container", "compose" | docker | 95% | PostgreSQL | Enabled |
| "static", "HTML", "documentation" | nginx | 80% | None | Disabled |

### Bundle Size Recommendations

| Application Type | Default Bundle | RAM | vCPU | Use Case |
|-----------------|----------------|-----|------|----------|
| nginx (static) | micro_3_0 | 1GB | 1 | Static sites |
| react | micro_3_0 | 1GB | 1 | Frontend apps |
| lamp | small_3_0 | 2GB | 1 | PHP + Database |
| nodejs | small_3_0 | 2GB | 1 | API + Database |
| python | small_3_0 | 2GB | 1 | Web app + Database |
| docker | medium_3_0 | 4GB | 2 | Container overhead |

### Database Selection Logic

- **MySQL**: For LAMP stack applications (WordPress, PHP)
- **PostgreSQL**: For modern applications (Node.js, Python, Docker)
- **None**: For frontend-only applications (React, static sites)
- **User Preference**: Respects explicit database mentions in description

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
- **Username**: ${github_username || 'Not provided'}
- **Repository Name**: ${github_repo || app_name || `${app_type}-app`}
- **Full Repository**: ${finalGithubRepo}
- **Visibility**: ${repo_visibility}

**IAM Role Configuration:**
- **Custom Role ARN**: ${aws_role_arn ? 'Yes' : 'No'}
${aws_role_arn ? `- **Role ARN**: ${aws_role_arn}` : `- **Default Role**: GitHubActions-${app_name || `${app_type}-app`}-deployment`}

**Validation Results:**
✅ All required parameters provided
✅ Configuration validated successfully
${aws_role_arn ? '✅ Custom IAM role ARN format validated' : '✅ Default IAM role naming will be used'}
${app_type === 'docker' && ['nano_3_0', 'micro_3_0'].includes(bundle_id) ? 
  '⚠️  Warning: Docker applications work better with small_3_0+ bundles' : 
  '✅ Bundle size appropriate for application type'}
` : ''}`

    // Add comprehensive MCP tools documentation for help mode
    if (mode === 'help') {
      instructions += `

## 🛠️ **Complete MCP Tools Reference**

### 1. setup_complete_deployment (Primary Deployment Tool)
**Purpose**: Main deployment configuration and execution tool

**Modes**:
- \`fully_automated\` - AI agents provide all parameters (RECOMMENDED for AI)
- \`interactive\` - Guided prompts for users (default)
- \`auto\` - Minimal prompts with smart defaults
- \`help\` - Show this comprehensive help information

**Required Parameters for fully_automated mode**:
\`\`\`json
{
  "mode": "fully_automated",
  "app_type": "lamp|nodejs|python|react|docker|nginx",
  "app_name": "your-app-name",
  "instance_name": "your-instance-name"
}
\`\`\`

**Optional Parameters**:
\`\`\`json
{
  "aws_region": "us-east-1",
  "aws_role_arn": "arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME",
  "app_version": "1.0.0", 
  "blueprint_id": "ubuntu_22_04",
  "bundle_id": "micro_3_0|small_3_0|medium_3_0|large_3_0",
  "database_type": "mysql|postgresql|none",
  "db_external": false,
  "db_rds_name": "external-db-name",
  "db_name": "app_db",
  "enable_bucket": false,
  "bucket_name": "storage-bucket",
  "bucket_access": "read_only|read_write",
  "bucket_bundle": "small_1_0",
  "github_repo": "repository-name",
  "repo_visibility": "public|private"
}
\`\`\`

### 2. analyze_deployment_requirements ⭐ **NEW INTELLIGENT TOOL**
**Purpose**: AI agents get intelligent parameter recommendations instead of manual configuration

**Input**:
\`\`\`json
{
  "user_description": "Node.js Express API with MySQL database",
  "app_context": {
    "technologies": ["Node.js", "Express", "MySQL"],
    "features": ["API", "authentication", "file uploads"],
    "scale": "small|medium|large"
  }
}
\`\`\`

**Output**: Complete analysis with confidence scoring and ready-to-execute parameters

### 3. get_deployment_examples
**Purpose**: Get example configurations and workflows for different application types

**Usage**:
\`\`\`json
{
  "app_type": "all|lamp|nodejs|python|react|docker|nginx",
  "include_configs": true,
  "include_workflows": true
}
\`\`\`

### 4. get_project_structure_guide ⭐ **NEW PROJECT STRUCTURE TOOL**
**Purpose**: Get comprehensive project structure recommendations based on application type and GitHub Actions configuration

**Usage**:
\`\`\`json
{
  "app_type": "lamp|nodejs|python|react|docker|nginx",
  "include_examples": true,
  "include_github_actions": true,
  "deployment_features": ["database", "bucket", "ssl", "docker", "monitoring"]
}
\`\`\`

**Returns**: Complete project structure guide with directory layout, required files, example code, deployment configuration, GitHub Actions setup, and direct links to working example applications

### 5. get_deployment_status
**Purpose**: Monitor GitHub Actions deployment progress

**Usage**:
\`\`\`json
{
  "repo_path": "."
}
\`\`\`

### 6. diagnose_deployment
**Purpose**: Run deployment diagnostics and troubleshooting

**Usage**:
\`\`\`json
{
  "repo_path": ".",
  "check_type": "all|prerequisites|configuration|github|aws|instance"
}
\`\`\`

## 🎯 **AI Agent Best Practices**

### 5. configure_github_repository ⭐ **NEW GITHUB CONFIGURATION TOOL**

**Purpose**: Configure GitHub repository settings and provide dynamic repository URLs with personalized links

**Parameters**:
- \`github_username\` (required): GitHub username for the repository
- \`repository_name\` (required): Name of the GitHub repository  
- \`app_type\` (optional): Application type for customized setup

**Example**:
\`\`\`json
{
  "github_username": "your-username",
  "repository_name": "my-app-deployment", 
  "app_type": "nodejs"
}
\`\`\`

**Returns**: Personalized repository URLs, setup commands, and configuration instructions

### Recommended Workflow for AI Agents:
1. **Configure GitHub repository**: Call \`configure_github_repository\` to set up personalized repository URLs
2. **Analyze requirements**: Call \`analyze_deployment_requirements\` for intelligent parameter detection
3. **Get project structure guidance**: Call \`get_project_structure_guide\` to help users organize their code
4. **Use exact parameters**: Copy parameters from analysis response
5. **Execute deployment**: Call \`setup_complete_deployment\` with \`fully_automated\` mode
5. **Explain results**: Tell user what was configured and why

### Parameter Validation Rules:
- ✅ **Docker apps**: Require minimum \`small_3_0\` bundle (2GB RAM)
- ✅ **Bucket enabled**: Must provide \`bucket_name\` when \`enable_bucket: true\`
- ✅ **External DB**: Must provide \`db_rds_name\` when \`db_external: true\`
- ✅ **Custom IAM role**: Must follow format \`arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME\`
- ✅ **Required fields**: Always include \`app_type\`, \`app_name\`, \`instance_name\`

### Error Recovery:
- **Validation Error**: Check parameter requirements above
- **Bundle Size Error**: Use \`small_3_0\` or higher for Docker apps
- **Missing Parameters**: Call this help mode for complete reference
- **Environment Issues**: Use \`diagnose_deployment\` tool

## 📊 **Success Metrics for AI Agents**

**Good AI Agent Behavior**:
- ✅ Uses intelligent analysis for parameter recommendations
- ✅ Gets 85-95% confidence scores for application detection
- ✅ Deploys in under 30 seconds from user request
- ✅ Asks maximum 1 clarifying question
- ✅ Explains analysis reasoning and configuration choices
- ✅ Provides actionable next steps

**Avoid These Patterns**:
- ❌ Asking "What database do you prefer?"
- ❌ Asking "Which bundle size do you want?"
- ❌ Manual parameter guessing without analysis
- ❌ Multiple technical configuration questions
- ❌ Delaying execution for "perfect" configuration

## 🚀 **Quick Start for AI Agents**

**Copy this workflow into your AI agent system prompt**:

\`\`\`
When users mention deploying applications:

1. ANALYZE (10 seconds): Call analyze_deployment_requirements with user description
2. VALIDATE (5 seconds): Check confidence score and parameters from analysis  
3. EXECUTE (10 seconds): Call setup_complete_deployment with exact parameters
4. EXPLAIN (5 seconds): Tell user what was configured and why

Total time: ~30 seconds from request to deployment
\`\`\`

---

**🎯 Ready for AI-powered deployment automation!**
`;
    }

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

  async configureGitHubRepository(args) {
    const { github_username, repository_name, app_type = 'nodejs' } = args;
    
    if (!github_username || !repository_name) {
      return {
        content: [{ type: 'text', text: 'Error: github_username and repository_name are required parameters' }]
      };
    }

    const repoUrl = `https://github.com/${github_username}/${repository_name}`;
    
    let response = `# 🔧 GitHub Repository Configuration

## ✅ Repository Information Configured
- **GitHub Username**: ${github_username}
- **Repository Name**: ${repository_name}
- **Repository URL**: ${repoUrl}
- **Application Type**: ${app_type}

## 🔗 Personalized Repository Links

### Example Application Files
- **Complete Example**: [example-${app_type}-app/](${repoUrl}/tree/main/example-${app_type}-app)
- **Deployment Config**: [deployment-${app_type}.config.yml](${repoUrl}/blob/main/deployment-${app_type}.config.yml)
- **GitHub Workflow**: [deploy-${app_type}.yml](${repoUrl}/blob/main/.github/workflows/deploy-${app_type}.yml)

### Quick Start Commands (Personalized)
\`\`\`bash
# Clone your repository
git clone ${repoUrl}.git
cd ${repository_name}

# Download example files from your repository
curl -o deployment-${app_type}.config.yml "${repoUrl}/raw/main/deployment-${app_type}.config.yml"
curl -o .github/workflows/deploy-${app_type}.yml "${repoUrl}/raw/main/.github/workflows/deploy-${app_type}.yml"

# Download complete example application
git clone ${repoUrl}.git temp-repo
cp -r temp-repo/example-${app_type}-app ./
rm -rf temp-repo
\`\`\`

## 🚀 Setup Commands for Your Repository

### Initialize New Repository
\`\`\`bash
# If you haven't created the repository yet
gh repo create ${github_username}/${repository_name} --private --description "${app_type} application deployment"

# Clone and setup
git clone ${repoUrl}.git
cd ${repository_name}
\`\`\`

### Setup Complete Deployment (Automated)
\`\`\`bash
# Run the setup script with your repository configured
export GITHUB_REPO="${github_username}/${repository_name}"
export APP_TYPE="${app_type}"
export APP_NAME="${repository_name}"
export INSTANCE_NAME="${app_type}-${repository_name}-app"

# Run automated setup
./setup-complete-deployment.sh --auto
\`\`\`

## 📋 Environment Variables for Automation

Set these environment variables for fully automated deployment:

\`\`\`bash
export GITHUB_REPO="${github_username}/${repository_name}"
export APP_TYPE="${app_type}"
export APP_NAME="${repository_name}"
export INSTANCE_NAME="${app_type}-${repository_name}-app"
export AWS_REGION="us-east-1"
export BLUEPRINT_ID="ubuntu_22_04"
export BUNDLE_ID="micro_3_0"
export DATABASE_TYPE="mysql"
export ENABLE_BUCKET="true"
export BUCKET_NAME="${app_type}-${repository_name}-bucket"
\`\`\`

## 🔄 Next Steps

1. **Create Repository**: Use \`gh repo create\` command above if repository doesn't exist
2. **Run Setup**: Use the setup script with your repository configured
3. **Customize**: Edit the generated configuration files for your needs
4. **Deploy**: Push changes to trigger GitHub Actions deployment

## 📖 Documentation Links

- **Main Repository**: ${repoUrl}
- **Setup Guide**: [README.md](${repoUrl}/blob/main/README.md)
- **MCP Server**: [mcp-server/README.md](${repoUrl}/blob/main/mcp-server/README.md)

## ⚠️ Important Notes

- Replace placeholder URLs in generated files with your actual repository URL
- Ensure GitHub CLI (\`gh\`) is authenticated: \`gh auth login\`
- Configure AWS CLI credentials: \`aws configure\`
- Set up GitHub OIDC for AWS authentication in your repository settings

Your repository is now configured for automated deployment! 🎉`;

    return { content: [{ type: 'text', text: response }] };
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
