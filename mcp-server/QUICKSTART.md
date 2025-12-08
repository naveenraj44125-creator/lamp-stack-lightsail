# MCP Server Quick Start

Get started with the Lightsail Deployment MCP Server in 5 minutes.

## Installation (30 seconds)

### Option 1: Zero Install with NPX (Easiest!)

No installation needed! Just add configuration.

### Option 2: Global Install

```bash
npm install -g lightsail-deployment-mcp
```

## Configuration (1 minute)

### For Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

**With NPX (no install needed):**
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

**With global install:**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "lightsail-deployment-mcp"
    }
  }
}
```

### For Kiro IDE

Create `.kiro/settings/mcp.json` in your workspace:

**With NPX (no install needed):**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "npx",
      "args": ["-y", "lightsail-deployment-mcp"],
      "disabled": false
    }
  }
}
```

**With global install:**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "lightsail-deployment-mcp",
      "disabled": false
    }
  }
}
```

## Verify Installation (30 seconds)

Restart your AI assistant and ask:

```
What Lightsail deployment tools are available?
```

You should see 6 tools listed.

## First Deployment (2 minutes)

### Option 1: New Project

Ask your AI assistant:

```
Create a new Node.js app called "my-api" deployed to Lightsail instance "my-api-prod" in us-east-1
```

Follow the steps provided by the AI.

### Option 2: Existing Project

Ask your AI assistant:

```
Add Lightsail deployment to my existing project at ./my-app for a React application
```

The AI will integrate deployment automation into your project.

## What You Get

✅ Complete GitHub Actions workflows
✅ Deployment configuration files
✅ Python deployment scripts
✅ OIDC authentication setup
✅ Health check monitoring
✅ Automatic deployments on push

## Next Steps

1. **Set up OIDC**: Ask AI to "Set up OIDC for my repository"
2. **Configure secrets**: Add AWS credentials to GitHub
3. **Push code**: Deployment triggers automatically
4. **Monitor**: Ask "What's my deployment status?"

## Common Commands

- "Create a new [app-type] app deployed to Lightsail"
- "Add Lightsail deployment to my existing repo"
- "Generate a deployment config for [app-type]"
- "Set up OIDC for my repository"
- "Check my deployment status"
- "What example applications are available?"
- "Diagnose my deployment setup" or "Troubleshoot deployment issues"

## Supported App Types

- `lamp` - Apache + PHP + MySQL/PostgreSQL
- `nginx` - Static sites and reverse proxy
- `nodejs` - Express, Next.js, NestJS
- `python` - Flask, Django, FastAPI
- `react` - CRA, Vite, Next.js static
- `docker` - Multi-container apps

## Troubleshooting

### Server not found

```bash
# Check installation
which lightsail-deployment-mcp

# Reinstall if needed
npm link
```

### Tools not showing

1. Restart your AI assistant
2. Check MCP configuration file
3. Verify Node.js version: `node --version` (18+)

### Need help?

Ask your AI assistant:

```
Diagnose my deployment setup
```

or

```
How do I use the Lightsail deployment tools?
```

## Full Documentation

- [README.md](README.md) - Complete documentation
- [INSTALL.md](INSTALL.md) - Detailed installation guide
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [CHANGELOG.md](CHANGELOG.md) - Version history

## Test Your Setup

```bash
# Run tests
./test.sh

# Should output:
# ✅ All tests passed!
```

---

**Ready to deploy?** Ask your AI assistant to get started! 🚀
