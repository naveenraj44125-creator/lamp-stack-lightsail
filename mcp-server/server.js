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
import { writeFileSync, existsSync } from 'fs';
import { join } from 'path';

const REPO_URL = 'https://github.com/naveenraj44125-creator/lamp-stack-lightsail.git';

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
          name: 'setup_new_repository',
          description: 'Create a new GitHub repository with Lightsail deployment automation. Supports multiple operating systems (Ubuntu, Amazon Linux, CentOS) and instance sizes (Nano to 2XLarge). The script will interactively prompt for OS and instance size selection.',
          inputSchema: {
            type: 'object',
            properties: {
              repo_name: { type: 'string', description: 'Repository name' },
              app_type: { type: 'string', enum: ['lamp', 'nginx', 'nodejs', 'python', 'react', 'docker'] },
              instance_name: { type: 'string', description: 'Lightsail instance name' },
              aws_region: { type: 'string', default: 'us-east-1' },
              blueprint_id: { 
                type: 'string', 
                description: 'Operating system blueprint (ubuntu_22_04, ubuntu_20_04, amazon_linux_2023, amazon_linux_2, centos_7_2009_01)',
                enum: ['ubuntu_22_04', 'ubuntu_20_04', 'amazon_linux_2023', 'amazon_linux_2', 'centos_7_2009_01'],
                default: 'ubuntu_22_04'
              },
              bundle_id: { 
                type: 'string', 
                description: 'Instance size bundle (nano_3_0, micro_3_0, small_3_0, medium_3_0, large_3_0, xlarge_3_0, 2xlarge_3_0)',
                enum: ['nano_3_0', 'micro_3_0', 'small_3_0', 'medium_3_0', 'large_3_0', 'xlarge_3_0', '2xlarge_3_0'],
                default: 'small_3_0'
              },
            },
            required: ['repo_name', 'app_type', 'instance_name'],
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
          name: 'integrate_lightsail_actions',
          description: 'Add Lightsail deployment automation to an existing GitHub repository. Supports multiple operating systems (Ubuntu, Amazon Linux, CentOS) and instance sizes (Nano to 2XLarge). The script will interactively configure deployment based on your application type.',
          inputSchema: {
            type: 'object',
            properties: {
              app_type: { type: 'string', enum: ['lamp', 'nginx', 'nodejs', 'python', 'react', 'docker'] },
              instance_name: { type: 'string', description: 'Lightsail instance name' },
              aws_region: { type: 'string', default: 'us-east-1' },
              blueprint_id: { 
                type: 'string', 
                description: 'Operating system blueprint (ubuntu_22_04, ubuntu_20_04, amazon_linux_2023, amazon_linux_2, centos_7_2009_01)',
                enum: ['ubuntu_22_04', 'ubuntu_20_04', 'amazon_linux_2023', 'amazon_linux_2', 'centos_7_2009_01'],
                default: 'ubuntu_22_04'
              },
              bundle_id: { 
                type: 'string', 
                description: 'Instance size bundle (nano_3_0, micro_3_0, small_3_0, medium_3_0, large_3_0, xlarge_3_0, 2xlarge_3_0)',
                enum: ['nano_3_0', 'micro_3_0', 'small_3_0', 'medium_3_0', 'large_3_0', 'xlarge_3_0', '2xlarge_3_0'],
                default: 'small_3_0'
              },
              repo_path: { type: 'string', description: 'Repository path (default: current directory)', default: '.' },
            },
            required: ['app_type', 'instance_name'],
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
          case 'setup_new_repository':
            return await this.setupNewRepository(args);
          case 'integrate_lightsail_actions':
            return await this.integrateLightsailActions(args);
          case 'get_deployment_status':
            return await this.getDeploymentStatus(args);
          case 'diagnose_deployment':
            return await this.diagnoseDeployment(args);
          default:
            return {
              content: [{ type: 'text', text: `Tool ${name} not yet implemented in HTTP mode. Use stdio mode for full functionality.` }],
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

  async setupNewRepository(args) {
    const { repo_name, app_type, instance_name, aws_region = 'us-east-1', blueprint_id = 'ubuntu_22_04', bundle_id = 'small_3_0' } = args;
    
    try {
      // Create a temporary script with the provided parameters
      const scriptContent = `#!/bin/bash
# Auto-generated setup script with MCP parameters
export REPO_NAME="${repo_name}"
export APP_TYPE="${app_type}"
export INSTANCE_NAME="${instance_name}"
export AWS_REGION="${aws_region}"
export BLUEPRINT_ID="${blueprint_id}"
export BUNDLE_ID="${bundle_id}"

# Run the setup script with environment variables
./setup-new-repo.sh
`;
      
      writeFileSync('/tmp/mcp-setup-repo.sh', scriptContent);
      execSync('chmod +x /tmp/mcp-setup-repo.sh');
      
      const output = execSync('/tmp/mcp-setup-repo.sh', { 
        encoding: 'utf-8',
        cwd: process.cwd(),
        timeout: 300000 // 5 minutes
      });
      
      return { 
        content: [{ 
          type: 'text', 
          text: `# Repository Setup Complete\n\n✅ Created repository: ${repo_name}\n✅ Application type: ${app_type}\n✅ Instance: ${instance_name} (${bundle_id})\n✅ Region: ${aws_region}\n✅ OS: ${blueprint_id}\n\n${output}` 
        }] 
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Setup failed: ${error.message}` }],
        isError: true,
      };
    }
  }

  async integrateLightsailActions(args) {
    const { app_type, instance_name, aws_region = 'us-east-1', blueprint_id = 'ubuntu_22_04', bundle_id = 'small_3_0', repo_path = '.' } = args;
    
    try {
      // Create a temporary script with the provided parameters
      const scriptContent = `#!/bin/bash
# Auto-generated integration script with MCP parameters
export APP_TYPE="${app_type}"
export INSTANCE_NAME="${instance_name}"
export AWS_REGION="${aws_region}"
export BLUEPRINT_ID="${blueprint_id}"
export BUNDLE_ID="${bundle_id}"

# Run the integration script with environment variables
./integrate-lightsail-actions.sh
`;
      
      writeFileSync('/tmp/mcp-integrate.sh', scriptContent);
      execSync('chmod +x /tmp/mcp-integrate.sh');
      
      const output = execSync('/tmp/mcp-integrate.sh', { 
        encoding: 'utf-8',
        cwd: repo_path,
        timeout: 300000 // 5 minutes
      });
      
      return { 
        content: [{ 
          type: 'text', 
          text: `# Lightsail Integration Complete\n\n✅ Application type: ${app_type}\n✅ Instance: ${instance_name} (${bundle_id})\n✅ Region: ${aws_region}\n✅ OS: ${blueprint_id}\n\n${output}` 
        }] 
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `❌ Integration failed: ${error.message}` }],
        isError: true,
      };
    }
  }

  async diagnoseDeployment(args) {
    const { repo_path = '.', check_type = 'all' } = args;
    let report = '# Deployment Diagnostics\n\n';
    
    // Basic checks
    try {
      const nodeVersion = execSync('node --version', { encoding: 'utf-8' }).trim();
      report += `✅ Node.js: ${nodeVersion}\n`;
    } catch (error) {
      report += '❌ Node.js: Not installed\n';
    }

    try {
      execSync('gh auth status', { encoding: 'utf-8', stdio: 'pipe' });
      report += '✅ GitHub CLI: Authenticated\n';
    } catch (error) {
      report += '❌ GitHub CLI: Not authenticated\n';
    }

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
                    <strong>setup_new_repository</strong><br>
                    Create GitHub repos with Lightsail deployment automation.<br>
                    <em>Supports multiple OS (Ubuntu, Amazon Linux, CentOS) and instance sizes (Nano to 2XLarge)</em>
                </div>
                <div class="tool">
                    <strong>integrate_lightsail_actions</strong><br>
                    Add Lightsail deployment to existing repositories.<br>
                    <em>Interactive configuration for OS, instance size, and application type</em>
                </div>
                <div class="tool">
                    <strong>get_deployment_status</strong><br>
                    Check deployment status and workflow runs
                </div>
                <div class="tool">
                    <strong>diagnose_deployment</strong><br>
                    Run deployment diagnostics and troubleshooting
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
