# Installation Guide - Choose Your Setup

Complete guide to help you choose the best installation method for your needs.

## Quick Comparison

| Method | Best For | Setup Time | Cost | Team Access |
|--------|----------|------------|------|-------------|
| **Remote Server** | Teams, Production | 5 min | $3.50-5/mo | ✅ Yes |
| **NPX** | Individual, Quick Start | 30 sec | Free | ❌ No |
| **Global Install** | Individual, Frequent Use | 1 min | Free | ❌ No |
| **Local Dev** | Development, Testing | 2 min | Free | ❌ No |

## Option 1: Remote Server on Lightsail ⭐ Recommended for Teams

### When to Use
- Multiple team members need access
- Want centralized deployment management
- Need always-available service
- Production environment

### Pros
- ✅ No local installation for team members
- ✅ Centralized updates
- ✅ Always available
- ✅ Secure with authentication
- ✅ Can use from any device
- ✅ Runs on smallest Lightsail instance ($3.50/mo)

### Cons
- ❌ Requires Lightsail instance
- ❌ Small monthly cost
- ❌ Needs basic server management

### Setup

**Quick Deploy:**
```bash
cd mcp-server
./deploy-to-lightsail.sh your-instance-ip
```

**Manual Deploy:**
See [DEPLOY.md](DEPLOY.md) for complete guide.

**Client Configuration:**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "url": "http://your-instance-ip:3000/sse",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

**Cost:**
- Lightsail instance: $3.50-5/month
- Can share with other services
- First 1TB data transfer free

---

## Option 2: NPX (Zero Install) ⭐ Recommended for Individuals

### When to Use
- Individual developer
- Quick start needed
- Don't want to manage installation
- Occasional use

### Pros
- ✅ Zero installation
- ✅ Always latest version
- ✅ No maintenance
- ✅ Works immediately
- ✅ Free

### Cons
- ❌ Slower first run (downloads package)
- ❌ Requires internet connection
- ❌ No team sharing

### Setup

**Configuration:**
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

**That's it!** No installation needed.

---

## Option 3: Global NPM Install

### When to Use
- Individual developer
- Frequent use
- Want faster startup
- Offline work needed

### Pros
- ✅ Fast startup
- ✅ Works offline
- ✅ One-time install
- ✅ Free

### Cons
- ❌ Manual updates needed
- ❌ Local installation required
- ❌ No team sharing

### Setup

**Install:**
```bash
npm install -g lightsail-deployment-mcp
```

**Configuration:**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "lightsail-deployment-mcp"
    }
  }
}
```

**Update:**
```bash
npm update -g lightsail-deployment-mcp
```

---

## Option 4: Local Development

### When to Use
- Contributing to development
- Testing changes
- Custom modifications needed

### Pros
- ✅ Full control
- ✅ Can modify code
- ✅ Test changes immediately
- ✅ Free

### Cons
- ❌ Manual setup
- ❌ Manual updates
- ❌ More maintenance

### Setup

**Install:**
```bash
cd mcp-server
npm install
npm link
```

**Configuration:**
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "lightsail-deployment-mcp"
    }
  }
}
```

Or use absolute path:
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-server/index.js"]
    }
  }
}
```

---

## Decision Tree

```
Do you have a team?
├─ Yes → Use Remote Server on Lightsail
└─ No
   └─ Do you use it frequently?
      ├─ Yes → Use Global Install
      └─ No → Use NPX
```

## Detailed Scenarios

### Scenario 1: Small Development Team (3-5 people)

**Recommendation:** Remote Server

**Why:**
- One-time setup benefits everyone
- Centralized management
- Cost: $5/month ÷ 5 people = $1/person
- No individual setup needed

**Setup:**
```bash
./deploy-to-lightsail.sh team-instance-ip
# Share token with team
```

### Scenario 2: Solo Developer, Daily Use

**Recommendation:** Global Install

**Why:**
- Fast startup
- Works offline
- One-time setup
- Free

**Setup:**
```bash
npm install -g lightsail-deployment-mcp
```

### Scenario 3: Trying It Out

**Recommendation:** NPX

**Why:**
- Zero setup
- No commitment
- Can switch later
- Free

**Setup:**
Just add config, no installation!

### Scenario 4: Contributing to Project

**Recommendation:** Local Development

**Why:**
- Can modify code
- Test changes
- Submit PRs

**Setup:**
```bash
git clone https://github.com/naveenraj44125-creator/lamp-stack-lightsail.git
cd lamp-stack-lightsail/mcp-server
npm install
npm link
```

## Migration Between Options

### From NPX to Global Install

```bash
# Just install globally
npm install -g lightsail-deployment-mcp

# Update config
# Change "command": "npx" to "command": "lightsail-deployment-mcp"
# Remove "args" field
```

### From Local to Remote Server

```bash
# Deploy to Lightsail
./deploy-to-lightsail.sh your-instance-ip

# Update all team configs to use HTTP endpoint
```

### From Global to Remote Server

```bash
# Deploy to Lightsail
./deploy-to-lightsail.sh your-instance-ip

# Update config to use HTTP endpoint
# Uninstall local: npm uninstall -g lightsail-deployment-mcp
```

## Troubleshooting

### NPX Issues

**Problem:** Slow startup
**Solution:** Use global install instead

**Problem:** Network errors
**Solution:** Check internet connection or use global install

### Global Install Issues

**Problem:** Command not found
**Solution:** Check npm global bin path
```bash
npm config get prefix
export PATH="$(npm config get prefix)/bin:$PATH"
```

### Remote Server Issues

**Problem:** Can't connect
**Solution:** Check firewall, verify port 3000 is open

**Problem:** Authentication failed
**Solution:** Verify token in config matches server token

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more help.

## Recommendations by Use Case

### For Companies/Teams
→ **Remote Server** - Best ROI, centralized management

### For Freelancers
→ **Global Install** - Fast, reliable, offline capable

### For Students/Learning
→ **NPX** - Zero commitment, easy to try

### For Open Source Contributors
→ **Local Development** - Full control, can contribute

### For CI/CD Pipelines
→ **NPX** - Consistent, always latest version

## Cost Analysis

### Remote Server (Team of 5)
- Instance: $5/month
- Per person: $1/month
- Setup time: 5 min (one time)
- Maintenance: 5 min/month

### NPX (Individual)
- Cost: $0
- Setup time: 30 seconds
- Maintenance: 0 (auto-updates)

### Global Install (Individual)
- Cost: $0
- Setup time: 1 minute
- Maintenance: 1 min/month (updates)

## Next Steps

1. **Choose your method** based on the guide above
2. **Follow setup instructions** for your chosen method
3. **Test the connection** with your AI assistant
4. **Read the documentation**:
   - [README.md](README.md) - Complete documentation
   - [QUICKSTART.md](QUICKSTART.md) - Quick start guide
   - [EXAMPLES.md](EXAMPLES.md) - Usage examples

---

**Still unsure?** Start with NPX - it's the easiest way to try it out!
