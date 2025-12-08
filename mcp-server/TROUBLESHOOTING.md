# Troubleshooting Guide

Complete troubleshooting guide for the Lightsail Deployment MCP Server.

## Installation Issues

### Command Not Found: `lightsail-deployment-mcp`

**Problem:** After running `npm link`, the command is not found.

**Solutions:**

1. Check npm global bin path:
```bash
npm config get prefix
```

2. Add to PATH (add to `~/.zshrc` or `~/.bashrc`):
```bash
export PATH="$(npm config get prefix)/bin:$PATH"
```

3. Reload shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

4. Verify installation:
```bash
which lightsail-deployment-mcp
```

### Permission Denied

**Problem:** `EACCES` error during `npm link`.

**Solutions:**

1. Use sudo (not recommended):
```bash
sudo npm link
```

2. Fix npm permissions (recommended):
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
npm link
```

### Node Version Error

**Problem:** "Node.js 18+ required" error.

**Solutions:**

1. Check current version:
```bash
node --version
```

2. Install Node.js 18+ using nvm:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

3. Or use Homebrew (macOS):
```bash
brew install node@18
```

## MCP Client Configuration Issues

### Tools Not Showing in AI Assistant

**Problem:** MCP server installed but tools don't appear.

**Solutions:**

1. Verify server is running:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | lightsail-deployment-mcp
```

2. Check MCP client config file location:
   - **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
   - **Kiro IDE**: `.kiro/settings/mcp.json` (workspace)

3. Verify config syntax:
```json
{
  "mcpServers": {
    "lightsail-deployment": {
      "command": "lightsail-deployment-mcp"
    }
  }
}
```

4. Restart your AI assistant completely

5. Check for config errors in client logs

### Server Connection Failed

**Problem:** MCP client can't connect to server.

**Solutions:**

1. Test server directly:
```bash
node mcp-server/index.js
```

2. Check for error messages in stderr

3. Verify dependencies installed:
```bash
cd mcp-server
npm install
```

4. Use absolute path in config:
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

### Server Crashes on Startup

**Problem:** Server starts then immediately crashes.

**Solutions:**

1. Check for syntax errors:
```bash
node --check mcp-server/index.js
```

2. Run with error output:
```bash
node mcp-server/index.js 2>&1
```

3. Verify SDK version:
```bash
npm list @modelcontextprotocol/sdk
```

4. Reinstall dependencies:
```bash
cd mcp-server
rm -rf node_modules package-lock.json
npm install
```

## Tool Execution Issues

### GitHub CLI Not Found

**Problem:** "gh: command not found" error.

**Solutions:**

1. Install GitHub CLI:
```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

2. Authenticate:
```bash
gh auth login
```

3. Verify:
```bash
gh auth status
```

### AWS CLI Not Found

**Problem:** "aws: command not found" for OIDC setup.

**Solutions:**

1. Install AWS CLI:
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

2. Configure credentials:
```bash
aws configure
```

3. Verify:
```bash
aws sts get-caller-identity
```

### Git Not Found

**Problem:** "git: command not found" error.

**Solutions:**

1. Install Git:
```bash
# macOS
brew install git

# Linux
sudo apt-get install git
```

2. Verify:
```bash
git --version
```

### Repository Clone Failed

**Problem:** Can't clone template repository.

**Solutions:**

1. Check internet connection

2. Verify repository URL:
```bash
curl -I https://github.com/naveenraj44125-creator/lamp-stack-lightsail.git
```

3. Check Git credentials:
```bash
git config --global user.name
git config --global user.email
```

4. Try manual clone:
```bash
git clone https://github.com/naveenraj44125-creator/lamp-stack-lightsail.git /tmp/test-clone
```

## Deployment Issues

### OIDC Authentication Failed

**Problem:** GitHub Actions can't authenticate with AWS.

**Solutions:**

1. Verify OIDC provider exists:
```bash
aws iam list-open-id-connect-providers
```

2. Check IAM role trust policy:
```bash
aws iam get-role --role-name GitHubActionsRole --query 'Role.AssumeRolePolicyDocument'
```

3. Verify GitHub variable is set:
```bash
gh variable list
```

4. Check repository name matches trust policy:
```json
"StringLike": {
  "token.actions.githubusercontent.com:sub": "repo:OWNER/REPO:ref:refs/heads/main"
}
```

5. Ensure role has required policies:
```bash
aws iam list-attached-role-policies --role-name GitHubActionsRole
```

### Deployment Workflow Failed

**Problem:** GitHub Actions workflow fails.

**Solutions:**

1. Check workflow logs:
```bash
gh run list --limit 5
gh run view <run-id> --log
```

2. Verify deployment config exists:
```bash
ls -la deployment-*.config.yml
```

3. Check Python dependencies:
```bash
python3 --version
pip3 list | grep boto3
```

4. Verify Lightsail instance exists:
```bash
aws lightsail get-instance --instance-name your-instance-name
```

5. Check instance is running:
```bash
aws lightsail get-instance-state --instance-name your-instance-name
```

### Health Check Timeout

**Problem:** Deployment succeeds but health check fails.

**Solutions:**

1. Check instance is accessible:
```bash
curl -I http://your-instance-ip
```

2. Verify firewall rules:
```bash
aws lightsail get-instance-port-states --instance-name your-instance-name
```

3. Check application logs on instance:
```bash
ssh ubuntu@your-instance-ip
sudo journalctl -u apache2 -n 50  # or nginx, docker, etc.
```

4. Increase health check timeout in config:
```yaml
monitoring:
  health_check:
    max_attempts: 20  # Increase from 10
```

### S3 Bucket Integration Failed

**Problem:** Bucket creation or attachment fails.

**Solutions:**

1. Verify bucket name is available:
```bash
aws lightsail get-buckets
```

2. Check IAM permissions for Lightsail buckets:
```bash
aws iam get-role-policy --role-name GitHubActionsRole --policy-name LightsailBucketAccess
```

3. Verify bucket bundle ID is valid:
```yaml
bucket:
  bundle_id: small_1_0  # Must be: small_1_0, medium_1_0, or large_1_0
```

4. Check bucket region matches instance region

### Database Connection Failed

**Problem:** Application can't connect to database.

**Solutions:**

1. For local database, check service is running:
```bash
ssh ubuntu@your-instance-ip
sudo systemctl status mysql  # or postgresql
```

2. For RDS, verify security group:
```bash
aws rds describe-db-instances --db-instance-identifier your-db-name
```

3. Check connection string in environment variables:
```bash
gh secret list
```

4. Verify database credentials are correct

5. Test connection from instance:
```bash
mysql -h localhost -u dbuser -p  # or psql
```

## Performance Issues

### Slow Deployment

**Problem:** Deployments take too long.

**Solutions:**

1. Check instance size:
```bash
aws lightsail get-instance --instance-name your-instance-name --query 'instance.bundleId'
```

2. Optimize dependency installation:
   - Use package caching
   - Minimize dependencies
   - Use production builds

3. Reduce health check attempts:
```yaml
monitoring:
  health_check:
    max_attempts: 5  # Reduce from 10
```

4. Enable parallel operations in workflow

### High Memory Usage

**Problem:** Instance runs out of memory.

**Solutions:**

1. Check current usage:
```bash
ssh ubuntu@your-instance-ip
free -h
```

2. Upgrade instance bundle:
```bash
aws lightsail create-instance-snapshot --instance-name your-instance
aws lightsail create-instances-from-snapshot --instance-names new-instance --bundle-id medium_2_0
```

3. Optimize application:
   - Reduce concurrent processes
   - Enable caching
   - Optimize database queries

4. Add swap space:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Debugging Tools

### Enable Verbose Logging

Add to workflow:
```yaml
- name: Deploy with Debug
  run: |
    python3 workflows/deploy-post-steps-generic.py
  env:
    DEBUG: true
```

### Test MCP Server Locally

```bash
# Test tools list
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node mcp-server/index.js

# Test specific tool
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_available_examples","arguments":{}}}' | node mcp-server/index.js
```

### Use MCP Inspector

```bash
npx @modelcontextprotocol/inspector node mcp-server/index.js
```

### Check Deployment Logs

```bash
# GitHub Actions logs
gh run list --limit 10
gh run view <run-id> --log

# Instance logs
ssh ubuntu@your-instance-ip
sudo journalctl -xe
sudo tail -f /var/log/syslog
```

### Verify Configuration

```bash
# Check deployment config
cat deployment-*.config.yml

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('deployment-lamp.config.yml'))"

# Check GitHub secrets
gh secret list

# Check GitHub variables
gh variable list
```

## Common Error Messages

### "Repository not found"

**Cause:** GitHub repository doesn't exist or no access.

**Fix:**
```bash
gh repo view OWNER/REPO  # Verify access
gh auth refresh  # Refresh authentication
```

### "Instance not found"

**Cause:** Lightsail instance doesn't exist.

**Fix:**
```bash
aws lightsail get-instances  # List all instances
aws lightsail create-instances --instance-names your-instance --bundle-id micro_2_0 --blueprint-id ubuntu_20_04
```

### "Permission denied (publickey)"

**Cause:** SSH key not configured.

**Fix:**
```bash
aws lightsail download-default-key-pair --region us-east-1 > lightsail-key.pem
chmod 400 lightsail-key.pem
ssh -i lightsail-key.pem ubuntu@your-instance-ip
```

### "Port 80 already in use"

**Cause:** Another service is using port 80.

**Fix:**
```bash
ssh ubuntu@your-instance-ip
sudo lsof -i :80  # Find process
sudo systemctl stop apache2  # or nginx
```

### "Docker daemon not running"

**Cause:** Docker service not started.

**Fix:**
```bash
ssh ubuntu@your-instance-ip
sudo systemctl start docker
sudo systemctl enable docker
```

## Getting Help

### Check Documentation

1. [README.md](README.md) - Main documentation
2. [EXAMPLES.md](EXAMPLES.md) - Usage examples
3. [INSTALL.md](INSTALL.md) - Installation guide
4. [QUICKSTART.md](QUICKSTART.md) - Quick start

### Run Diagnostics

```bash
cd mcp-server
./test.sh
```

### Report Issues

When reporting issues, include:

1. Node.js version: `node --version`
2. npm version: `npm --version`
3. Operating system
4. MCP client (Claude, Kiro, etc.)
5. Error messages (full output)
6. Steps to reproduce
7. Configuration files (sanitized)

### Community Support

- GitHub Issues: https://github.com/naveenraj44125-creator/lamp-stack-lightsail/issues
- Check existing issues for solutions
- Provide detailed information when creating new issues

## Prevention Tips

1. **Keep dependencies updated:**
```bash
npm update
```

2. **Test before deploying:**
```bash
./test.sh
```

3. **Use version control:**
```bash
git commit -am "Working configuration"
```

4. **Monitor deployments:**
```bash
gh run watch
```

5. **Regular backups:**
```bash
aws lightsail create-instance-snapshot --instance-name your-instance
```

6. **Document changes:**
   - Keep CHANGELOG.md updated
   - Comment configuration changes
   - Track deployment history

---

**Still having issues?** Ask your AI assistant for help with specific error messages!
