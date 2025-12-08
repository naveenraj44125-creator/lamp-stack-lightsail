# Testing Your Deployed MCP Server

Your MCP server is now deployed and running at: **http://52.202.252.239:3000**

## Quick Health Check

```bash
curl http://52.202.252.239:3000/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "lightsail-deployment-mcp",
  "version": "1.1.0"
}
```

## Testing Methods

### 1. Using the Test Scripts

#### Bash Test Script
```bash
cd mcp-server
./test-mcp-server.sh
```

#### Node.js Test Client
```bash
cd mcp-server
node test-mcp-client.js
```

### 2. Using MCP Inspector (Recommended)

The MCP Inspector is the official tool for testing MCP servers:

```bash
npx @modelcontextprotocol/inspector http://52.202.252.239:3000
```

This will open an interactive web interface where you can:
- List available tools
- Call tools with parameters
- See real-time responses
- Test the SSE connection

### 3. Using Claude Desktop

Add this to your Claude Desktop MCP configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://52.202.252.239:3000",
      "transport": "sse"
    }
  }
}
```

Then restart Claude Desktop and you'll see the MCP tools available.

### 4. Using curl (Manual Testing)

Test the SSE endpoint:
```bash
curl -N http://52.202.252.239:3000/sse
```

Send a message (requires SSE connection first):
```bash
curl -X POST http://52.202.252.239:3000/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

## Available MCP Tools

Your server provides these tools:

1. **setup_new_repository**
   - Create a new GitHub repository with Lightsail deployment automation
   - Parameters: repo_name, app_type, instance_name, aws_region

2. **deploy_to_lightsail**
   - Deploy an application to Lightsail
   - Parameters: instance_name, app_type, source_path

3. **list_instances**
   - List all Lightsail instances in your AWS account
   - Parameters: aws_region

4. **get_deployment_status**
   - Check the status of a deployment
   - Parameters: instance_name

## Server Endpoints

- **Health Check**: `GET /health`
- **SSE Connection**: `GET /sse`
- **MCP Messages**: `POST /message`

## Troubleshooting

### Server Not Responding

Run the debug script:
```bash
source .aws-creds.sh
python3 troubleshooting-tools/mcp-server/debug-mcp-server.py
# Enter: mcp-server-lightsail
# Enter: us-east-1
```

### Check Service Status

SSH into the instance:
```bash
ssh ubuntu@52.202.252.239
sudo systemctl status nodejs-app.service
sudo journalctl -u nodejs-app.service -n 50
```

### View Logs

```bash
ssh ubuntu@52.202.252.239
sudo tail -f /var/log/nodejs-app/output.log
sudo tail -f /var/log/nodejs-app/error.log
```

## Security Notes

⚠️ **Important**: This server is currently running without authentication. For production use:

1. Set an authentication token:
   ```bash
   # On the server
   export MCP_AUTH_TOKEN="your-secure-token"
   ```

2. Update the systemd service to include the token:
   ```bash
   sudo systemctl edit nodejs-app.service
   # Add: Environment="MCP_AUTH_TOKEN=your-secure-token"
   ```

3. Use the token in your client:
   ```bash
   curl -H "Authorization: Bearer your-secure-token" \
     http://52.202.252.239:3000/health
   ```

## Next Steps

1. ✅ Server is deployed and running
2. 🧪 Test with MCP Inspector: `npx @modelcontextprotocol/inspector http://52.202.252.239:3000`
3. 🔧 Configure in Claude Desktop (see above)
4. 🔒 Add authentication for production use
5. 📊 Monitor logs and performance

## Support

For issues or questions:
- Check the troubleshooting guide: `troubleshooting-tools/mcp-server/README.md`
- Review server logs on the instance
- Run the debug script for detailed diagnostics
