# MCP Server Troubleshooting Tools

Tools for debugging and fixing MCP Server deployments on AWS Lightsail.

## Prerequisites

```bash
# Install AWS CLI and configure credentials
pip install boto3

# Set up AWS credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

## Debug Script

Comprehensive diagnostic tool that checks:
- Node.js and npm versions
- Application files and structure
- systemd service status and configuration
- Service logs (journalctl and application logs)
- Port 3000 connectivity
- Process status
- File permissions

### Usage

```bash
python3 troubleshooting-tools/mcp-server/debug-mcp-server.py
```

You'll be prompted for:
- Instance name (default: mcp-server-demo)
- AWS region (default: us-east-1)

### What It Checks

1. **Node.js Environment**: Verifies Node.js and npm are installed
2. **Application Files**: Lists files in `/opt/nodejs-app/`
3. **Dependencies**: Shows installed npm packages
4. **Service Status**: Checks systemd service state
5. **Service Configuration**: Shows the systemd unit file
6. **Logs**: Displays recent service and application logs
7. **Process Status**: Shows running Node.js processes
8. **Port Binding**: Checks if port 3000 is listening
9. **Local Connectivity**: Tests HTTP connection to localhost:3000
10. **Permissions**: Verifies file ownership and permissions

## Common Issues

### Service Not Starting

**Symptoms**: Service fails to start or immediately exits

**Check**:
```bash
sudo journalctl -u nodejs-app.service -n 50
```

**Common Causes**:
- Wrong entry point file (app.js vs server.js vs index.js)
- Missing dependencies (npm install not run)
- Port already in use
- Permission issues

### Port Not Listening

**Symptoms**: No process listening on port 3000

**Check**:
```bash
sudo netstat -tlnp | grep :3000
```

**Common Causes**:
- Service not running
- Application crashed
- Wrong port configuration
- Firewall blocking

### Application Crashes

**Symptoms**: Service starts but immediately stops

**Check**:
```bash
sudo tail -50 /var/log/nodejs-app/error.log
```

**Common Causes**:
- Missing environment variables
- Dependency errors
- Code errors
- Port binding failures

## Manual Testing

Test the application manually:

```bash
# SSH into instance
ssh ubuntu@<instance-ip>

# Navigate to app directory
cd /opt/nodejs-app

# Run manually
node server.js

# Test locally
curl http://localhost:3000/
```

## Service Management

```bash
# Check service status
sudo systemctl status nodejs-app.service

# View logs
sudo journalctl -u nodejs-app.service -f

# Restart service
sudo systemctl restart nodejs-app.service

# Stop service
sudo systemctl stop nodejs-app.service

# Start service
sudo systemctl start nodejs-app.service
```
