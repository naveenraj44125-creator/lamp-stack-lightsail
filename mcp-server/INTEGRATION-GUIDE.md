# MCP Server Integration Guide

Complete guide for integrating the Lightsail Deployment MCP Server with AI assistants and development tools.

## 🚀 Quick Start

The MCP server is currently deployed and running at:
- **Server URL**: `http://18.215.231.164:3000`
- **Health Check**: `http://18.215.231.164:3000/health`
- **SSE Endpoint**: `http://18.215.231.164:3000/sse`

## 📋 Client Configurations

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://18.215.231.164:3000/sse",
      "transport": "sse"
    }
  }
}
```

**Location of config file:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Amazon Q Developer

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://18.215.231.164:3000/sse",
      "transport": "sse",
      "name": "Lightsail Deployment",
      "description": "AWS Lightsail deployment automation"
    }
  }
}
```

### Kiro IDE

Add to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://18.215.231.164:3000/sse",
      "transport": "sse",
      "disabled": false,
      "autoApprove": [
        "list_available_examples",
        "get_deployment_status",
        "diagnose_deployment"
      ]
    }
  }
}
```

### Continue.dev

Add to your `config.json`:

```json
{
  "mcpServers": [
    {
      "name": "lightsail-deployment",
      "url": "http://18.215.231.164:3000/sse",
      "transport": "sse"
    }
  ]
}
```

### Cursor IDE

Add to your MCP settings:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://18.215.231.164:3000/sse",
      "transport": "sse"
    }
  }
}
```

## 🔧 Testing the Connection

### 1. Health Check

Test if the server is running:

```bash
curl http://18.215.231.164:3000/health
```

Expected response:
```json
{"status":"ok","service":"lightsail-deployment-mcp","version":"1.1.0"}
```

### 2. Web Interface

Visit the web interface in your browser:
```
http://18.215.231.164:3000/
```

You should see a landing page with server information and configuration examples.

### 3. SSE Endpoint

Test the SSE endpoint (this will timeout, which is expected):
```bash
curl http://18.215.231.164:3000/sse
```

## 🛠️ Available Tools

Once connected, you'll have access to these 7 tools:

1. **setup_new_repository** - Create new GitHub repos with deployment automation
2. **integrate_existing_repository** - Add deployment to existing repos
3. **generate_deployment_config** - Generate configuration files
4. **setup_oidc_authentication** - Configure GitHub Actions with AWS
5. **get_deployment_status** - Check deployment status
6. **list_available_examples** - List available app templates
7. **diagnose_deployment** - Troubleshoot deployment issues

## 💬 Example Conversations

### Setting Up a New Project

**You:** "Create a new Node.js API called 'user-service' and deploy it to Lightsail"

**AI:** Will use the `setup_new_repository` tool to create a complete setup with:
- GitHub repository structure
- Deployment workflows
- Configuration files
- Step-by-step instructions

### Checking Deployment Status

**You:** "What's the status of my deployments?"

**AI:** Will use the `get_deployment_status` tool to show:
- Recent workflow runs
- Success/failure status
- Links to GitHub Actions
- Deployment timing

### Troubleshooting

**You:** "My deployment isn't working, can you help?"

**AI:** Will use the `diagnose_deployment` tool to check:
- Prerequisites (Node.js, GitHub CLI, AWS CLI)
- Configuration files
- GitHub authentication
- AWS credentials
- Common issues

## 🔐 Security Considerations

### Current Setup
- **Authentication**: Currently disabled for testing
- **Network**: Open to internet on port 3000
- **HTTPS**: Not configured (HTTP only)

### Production Recommendations
1. **Enable Authentication**: Set `MCP_AUTH_TOKEN` environment variable
2. **Use HTTPS**: Configure SSL/TLS certificates
3. **Firewall Rules**: Restrict access to specific IPs
4. **VPN Access**: Use VPN for secure access

### Enabling Authentication

If authentication is enabled on the server, update your client config:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://18.215.231.164:3000/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer YOUR_AUTH_TOKEN"
      }
    }
  }
}
```

## 🚨 Troubleshooting

### Connection Issues

**Problem**: Cannot connect to MCP server
**Solutions**:
1. Check if server is running: `curl http://18.215.231.164:3000/health`
2. Verify your client configuration
3. Check firewall settings
4. Ensure correct URL and port

### Authentication Errors

**Problem**: 401 Unauthorized
**Solutions**:
1. Check if authentication is enabled on server
2. Verify your auth token in headers
3. Contact server administrator for token

### Tool Execution Errors

**Problem**: Tools fail to execute
**Solutions**:
1. Check GitHub CLI authentication: `gh auth status`
2. Verify AWS credentials: `aws sts get-caller-identity`
3. Ensure you're in a Git repository
4. Use the `diagnose_deployment` tool

## 📊 Server Status

### Current Deployment
- **Instance**: mcp-server-lightsail-v6
- **IP Address**: 18.215.231.164
- **Port**: 3000
- **Status**: ✅ Running
- **Version**: 1.1.0
- **Last Updated**: December 10, 2025

### Monitoring

Check server status anytime:
```bash
# Health check
curl http://18.215.231.164:3000/health

# Server info (web interface)
curl http://18.215.231.164:3000/
```

## 🔄 Updates and Maintenance

The MCP server is automatically updated when changes are pushed to the main branch. The deployment process:

1. Code changes pushed to GitHub
2. GitHub Actions triggers deployment
3. Server automatically restarts with new version
4. No client reconfiguration needed

## 📞 Support

### Getting Help
1. **Documentation**: Check README.md and EXAMPLES.md
2. **Diagnostics**: Use the `diagnose_deployment` tool
3. **GitHub Issues**: Report bugs and feature requests
4. **Server Logs**: Available on the Lightsail instance

### Common Issues
- **GitHub CLI not authenticated**: Run `gh auth login`
- **AWS credentials missing**: Run `aws configure`
- **Repository not found**: Ensure you're in a Git repository
- **Permission denied**: Check GitHub repository permissions

## 🎯 Best Practices

1. **Test Connection First**: Always verify the server is responding
2. **Use Diagnostics**: Run diagnostics before reporting issues
3. **Keep Tools Updated**: Ensure GitHub CLI and AWS CLI are current
4. **Follow Examples**: Use the provided examples as templates
5. **Monitor Deployments**: Regularly check deployment status

## 📈 Performance

### Server Specifications
- **Instance Type**: Lightsail small_3_0 (2GB RAM, 2 vCPU)
- **Operating System**: Ubuntu 22.04 LTS
- **Node.js Version**: 18.x
- **Process Manager**: PM2

### Expected Response Times
- **Health Check**: < 100ms
- **Tool Execution**: 1-30 seconds (depending on complexity)
- **GitHub Operations**: 2-10 seconds
- **AWS Operations**: 1-5 seconds

---

**Ready to get started?** Add the MCP server to your AI assistant and try asking: *"What example applications can I deploy to Lightsail?"*