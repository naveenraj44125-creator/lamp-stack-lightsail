# MCP Server Installation Guide

## Quick Install

### For Claude Desktop

**Option 1: NPX (No Installation - Recommended)**

1. Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "npx",
      "args": ["-y", "lightsail-deployment-mcp"]
    }
  }
}
```

2. Restart Claude Desktop

**Option 2: Global Install**

1. Install globally:
```bash
npm install -g lightsail-deployment-mcp
```

2. Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "lightsail-deployment-mcp"
    }
  }
}
```

3. Restart Claude Desktop

### For Kiro IDE

**Option 1: NPX (No Installation - Recommended)**

1. Add to Kiro MCP config (`.kiro/settings/mcp.json` in your workspace):
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "npx",
      "args": ["-y", "lightsail-deployment-mcp"],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

2. Reload MCP servers in Kiro

**Option 2: Global Install**

1. Install globally:
```bash
npm install -g lightsail-deployment-mcp
```

2. Add to Kiro MCP config:
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "lightsail-deployment-mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

3. Reload MCP servers in Kiro

### For Other MCP Clients

**With NPX (no install):**
```json
{
  "command": "npx",
  "args": ["-y", "lightsail-deployment-mcp"]
}
```

**With global install:**
```bash
npm install -g lightsail-deployment-mcp
```

Then use:
```json
{
  "command": "lightsail-deployment-mcp"
}
```

**For local development:**
```json
{
  "command": "node",
  "args": ["/path/to/mcp-server/index.js"]
}
```

## Prerequisites

- Node.js 18 or higher
- GitHub CLI (`gh`) installed and authenticated
- AWS CLI configured (for OIDC setup)
- Git

## Verify Installation

After installation, ask your AI assistant:

```
What Lightsail deployment tools are available?
```

You should see 6 tools listed:
- setup_new_repository
- integrate_existing_repository
- generate_deployment_config
- setup_oidc_authentication
- get_deployment_status
- list_available_examples

## Troubleshooting

### Command not found

If `lightsail-deployment-mcp` is not found after `npm link`:

1. Check npm global bin path:
```bash
npm config get prefix
```

2. Add to PATH if needed:
```bash
export PATH="$(npm config get prefix)/bin:$PATH"
```

### Permission errors

Run with sudo if needed:
```bash
sudo npm link
```

### MCP server not connecting

1. Check Node.js version:
```bash
node --version  # Should be 18+
```

2. Test server directly:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | lightsail-deployment-mcp
```

3. Check MCP client logs for errors

## Uninstall

```bash
npm unlink -g lightsail-deployment-mcp
cd mcp-server
npm uninstall
```

## Development Mode

For testing changes:

```bash
cd mcp-server
npm install
node index.js
```

Use MCP Inspector for debugging:
```bash
npx @modelcontextprotocol/inspector node index.js
```
