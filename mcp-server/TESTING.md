# Testing the MCP Server

Complete guide for testing the Lightsail Deployment MCP Server.

## Quick Test

Verify the server is running:

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

## Full Protocol Test

Run the comprehensive SSE test:

```bash
node test-mcp-sse.js
```

This tests:
- ✅ SSE connection establishment
- ✅ MCP protocol initialization
- ✅ Tools discovery
- ✅ Tool execution
- ✅ JSON-RPC 2.0 responses

Expected output:
```
🧪 Testing MCP Server with SSE Protocol
========================================

1️⃣  Connecting to SSE endpoint...
   ✅ SSE connection established
   📍 Message endpoint: /message?sessionId=...
   🔑 Session ID: ...

2️⃣  Sending initialize command...
   Status: 202
   📨 Received message: {...}

3️⃣  Requesting tools list...
   Status: 202
   📨 Received message: {...}

✅ Test completed!
📊 Summary: Received 3 messages
```

## Available Tools

The server provides these tools:

1. **setup_new_repository**
   - Create GitHub repo with Lightsail deployment automation
   - Params: `repo_name`, `app_type`, `instance_name`, `aws_region`

2. **get_deployment_status**
   - Check deployment status
   - Params: `repo_path`

3. **diagnose_deployment**
   - Run deployment diagnostics
   - Params: `repo_path`, `check_type`

## Client Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://52.202.252.239:3000/sse"
    }
  }
}
```

### Cline / Other MCP Clients

Use the same SSE endpoint URL: `http://52.202.252.239:3000/sse`

## Troubleshooting

### Debug Script

Run comprehensive diagnostics:

```bash
python3 troubleshooting-tools/mcp-server/debug-mcp-server.py
```

Enter:
- Instance name: `mcp-server-lightsail`
- Region: `us-east-1`

### Check Service Status

On the Lightsail instance:

```bash
# Service status
sudo systemctl status nodejs-app.service

# Recent logs
sudo journalctl -u nodejs-app.service -n 50

# Application logs
sudo tail -50 /var/log/nodejs-app/output.log
sudo tail -50 /var/log/nodejs-app/error.log
```

### Common Issues

**Connection timeout:**
- Check firewall allows port 3000
- Verify instance is running
- Test health endpoint first

**SSE not working:**
- Ensure using `/sse` endpoint
- Check for session ID in response
- Verify POST to `/message?sessionId=...`

**Tool execution fails:**
- Check server logs for errors
- Verify tool parameters match schema
- Ensure AWS credentials configured (if needed)

## Test Checklist

- [x] Health endpoint responds
- [x] SSE connection establishes
- [x] Initialize handshake completes
- [x] Tools list returns correctly
- [x] Tool execution works
- [x] JSON-RPC 2.0 format correct
- [x] Error handling proper
- [x] Server handles disconnections
