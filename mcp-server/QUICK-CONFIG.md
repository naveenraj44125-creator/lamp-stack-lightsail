# Quick MCP Configuration

## Amazon Q - Copy & Paste Config

### Remote Server (Recommended)

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://52.202.252.239:3000/sse",
      "transport": "sse",
      "description": "AWS Lightsail deployment automation"
    }
  }
}
```

**Where to add:**
- **VS Code**: Settings → Search "Amazon Q MCP" → Edit settings.json
- **Amazon Q Desktop**: Settings → Developer Settings → MCP Configuration

### Local/NPX (Alternative)

```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "npx",
      "args": ["-y", "lightsail-deployment-mcp"],
      "transport": "stdio"
    }
  }
}
```

## Verify It Works

1. **Restart Amazon Q**
2. **Ask:** "List available MCP tools"
3. **Should see:** setup_new_repository, get_deployment_status, diagnose_deployment

## Test Commands

```
Create a new Node.js repository for Lightsail deployment

Check my deployment status

Diagnose deployment issues
```

## Troubleshooting

**Not working?**
```bash
# Test server
curl http://52.202.252.239:3000/health

# Should return: {"status":"ok",...}
```

**Need help?** See [AMAZON-Q-SETUP.md](AMAZON-Q-SETUP.md)
