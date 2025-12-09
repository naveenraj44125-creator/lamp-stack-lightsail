# Amazon Q Configuration for MCP Server

Complete guide to configure the Lightsail Deployment MCP Server with Amazon Q.

## Prerequisites

- Amazon Q Developer installed (VS Code extension or standalone)
- MCP server deployed and running (http://52.202.252.239:3000)
- Access to Amazon Q settings

## Configuration Methods

### Method 1: Remote Server (HTTP/SSE) - Recommended

This connects to your deployed Lightsail MCP server.

#### Step 1: Locate Amazon Q MCP Configuration

**For VS Code:**
1. Open VS Code
2. Go to Settings (Cmd+, on Mac, Ctrl+, on Windows)
3. Search for "Amazon Q MCP"
4. Click "Edit in settings.json"

**For Amazon Q Desktop:**
1. Open Amazon Q
2. Go to Settings → Developer Settings
3. Find "Model Context Protocol" section

#### Step 2: Add Server Configuration

Add this to your MCP configuration file:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://52.202.252.239:3000/sse",
      "transport": "sse",
      "description": "AWS Lightsail deployment automation tools"
    }
  }
}
```

**With Authentication (if enabled):**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://52.202.252.239:3000/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      },
      "description": "AWS Lightsail deployment automation tools"
    }
  }
}
```

### Method 2: Local Server (stdio) - For Development

Run the MCP server locally via stdio protocol.

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "node",
      "args": ["/path/to/mcp-server/index.js"],
      "transport": "stdio",
      "description": "AWS Lightsail deployment automation tools"
    }
  }
}
```

### Method 3: NPX (Zero Install)

Use npx to run without installation:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "npx",
      "args": ["-y", "lightsail-deployment-mcp"],
      "transport": "stdio",
      "description": "AWS Lightsail deployment automation tools"
    }
  }
}
```

## Configuration File Locations

### macOS
- **VS Code**: `~/Library/Application Support/Code/User/settings.json`
- **Amazon Q**: `~/.amazon-q/mcp.json`

### Windows
- **VS Code**: `%APPDATA%\Code\User\settings.json`
- **Amazon Q**: `%USERPROFILE%\.amazon-q\mcp.json`

### Linux
- **VS Code**: `~/.config/Code/User/settings.json`
- **Amazon Q**: `~/.amazon-q/mcp.json`

## Verify Configuration

### Step 1: Restart Amazon Q

After adding the configuration, restart Amazon Q or reload the VS Code window.

### Step 2: Check Server Connection

In Amazon Q chat, try:
```
List available MCP tools
```

You should see:
- setup_new_repository
- get_deployment_status
- diagnose_deployment

### Step 3: Test a Tool

Try using a tool:
```
Use the get_deployment_status tool to check my deployments
```

## Available Tools

Once configured, Amazon Q can use these tools:

### 1. setup_new_repository
Create a new GitHub repository with Lightsail deployment automation.

**Example prompt:**
```
Create a new repository called "my-nodejs-app" for a Node.js application 
that will deploy to a Lightsail instance named "nodejs-prod" in us-east-1
```

### 2. get_deployment_status
Check the status of GitHub Actions deployments.

**Example prompt:**
```
Check the deployment status for my repository
```

### 3. diagnose_deployment
Run diagnostics on deployment configuration.

**Example prompt:**
```
Diagnose deployment issues in my current repository
```

## Troubleshooting

### Server Not Connecting

**Check server health:**
```bash
curl http://52.202.252.239:3000/health
```

Expected response:
```json
{"status":"ok","service":"lightsail-deployment-mcp","version":"1.1.0"}
```

### Tools Not Appearing

1. **Verify configuration syntax** - JSON must be valid
2. **Check server URL** - Ensure it's accessible
3. **Restart Amazon Q** - Reload the extension/app
4. **Check logs** - Look for MCP connection errors

### Amazon Q Logs

**VS Code:**
1. Open Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
2. Type "Developer: Show Logs"
3. Select "Amazon Q"

**Look for:**
- MCP connection attempts
- Server handshake messages
- Tool registration confirmations

### Connection Timeout

If you get timeout errors:

1. **Check firewall** - Port 3000 must be open
2. **Verify server is running:**
   ```bash
   python3 troubleshooting-tools/mcp-server/debug-mcp-server.py
   ```
3. **Test SSE endpoint:**
   ```bash
   curl -N http://52.202.252.239:3000/sse
   ```

## Security Considerations

### For Production Use

1. **Enable Authentication:**
   Set `MCP_AUTH_TOKEN` environment variable on the server

2. **Use HTTPS:**
   Set up a reverse proxy with SSL:
   ```json
   {
     "mcpServers": {
       "lightsail-deployment": {
         "url": "https://your-domain.com/sse"
       }
     }
   }
   ```

3. **Restrict Access:**
   Configure Lightsail firewall to allow only your IP

### Environment Variables

If your tools need AWS credentials, set them on the server:

```bash
# On Lightsail instance
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

## Example Usage in Amazon Q

Once configured, you can interact naturally:

**User:** "I need to deploy a React app to AWS Lightsail"

**Amazon Q:** *Uses setup_new_repository tool to create the repo with deployment automation*

**User:** "Check if my deployment succeeded"

**Amazon Q:** *Uses get_deployment_status tool to check GitHub Actions*

**User:** "Something's wrong with my deployment"

**Amazon Q:** *Uses diagnose_deployment tool to identify issues*

## Advanced Configuration

### Multiple Environments

Configure different servers for dev/prod:

```json
{
  "mcpServers": {
    "lightsail-dev": {
      "url": "http://dev-server:3000/sse",
      "description": "Development environment"
    },
    "lightsail-prod": {
      "url": "http://52.202.252.239:3000/sse",
      "description": "Production environment"
    }
  }
}
```

### Custom Timeout

Increase timeout for slow connections:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://52.202.252.239:3000/sse",
      "timeout": 60000,
      "description": "AWS Lightsail deployment automation"
    }
  }
}
```

## Getting Help

- **Test the server:** `node mcp-server/test-mcp-sse.js`
- **Debug script:** `python3 troubleshooting-tools/mcp-server/debug-mcp-server.py`
- **Documentation:** See [TESTING.md](TESTING.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## AWS Console Q Chat

**Important:** Amazon Q in the AWS Console browser does **NOT** support MCP servers.

### Limitations
- ❌ AWS Console Q Chat cannot connect to MCP servers
- ❌ No custom tool integration in browser
- ❌ Only built-in AWS knowledge available

### Alternatives

**Option 1: Use Amazon Q Developer (Recommended)**
- Install VS Code extension
- Full MCP support
- Configure as shown above

**Option 2: Custom Web Interface**
- See `web-interface-example.html` for a simple chat UI
- Connects directly to your MCP server
- Can be hosted anywhere

**Option 3: API Integration**
- Call MCP server directly from your applications
- Use the HTTP/SSE endpoints
- Build custom workflows

## Next Steps

1. ✅ Configure Amazon Q Developer (not Console Q)
2. ✅ Restart Amazon Q
3. ✅ Verify tools are available
4. ✅ Try creating a test repository
5. ✅ Monitor deployment status

Your MCP server is ready to enhance Amazon Q Developer with Lightsail deployment capabilities!
