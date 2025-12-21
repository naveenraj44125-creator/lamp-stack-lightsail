# Deployment Monitoring and Verification Guide

## Overview

This guide covers the enhanced monitoring and verification tools for all deployment endpoints, including automatic detection and fixing of nginx default page issues.

## Tools Available

### 1. Enhanced Monitor Script (`monitor-all-deployments.sh`)

**Features:**
- Real-time GitHub Actions workflow monitoring
- Interactive commands for endpoint verification
- Automatic refresh every 30 seconds
- Clean, formatted output with status icons

**Usage:**
```bash
./monitor-all-deployments.sh
```

**Interactive Commands:**
- Press `v` + Enter: Run endpoint verification
- Press `f` + Enter: Get nginx fix instructions
- Press `q` + Enter: Quit monitoring
- Ctrl+C: Stop monitoring

### 2. Quick Endpoint Check (`quick-endpoint-check.py`)

**Features:**
- Fast verification of all deployment endpoints
- Automatic nginx default page detection
- Clear status reporting with actionable recommendations
- No AWS credentials required

**Usage:**
```bash
python3 quick-endpoint-check.py
```

**Output:**
- ✅ Working endpoints
- ❌ Failed endpoints with specific error types
- ⚠️ Nginx default page detection with fix recommendations

### 3. Comprehensive Endpoint Verifier (`verify-all-endpoints.py`)

**Features:**
- Advanced endpoint testing with AWS integration
- Automatic nginx configuration fixes via SSH/SSM
- Detailed error reporting and fix attempts
- Requires AWS credentials and SSH access

**Usage:**
```bash
# Verification only (no fixes)
python3 verify-all-endpoints.py --no-fix

# With automatic nginx fixes
python3 verify-all-endpoints.py --fix-nginx
```

## Current Deployment Status

### ✅ Working Deployments
1. **React Dashboard** - http://35.171.85.222/
   - Status: ✅ Fully functional
   - Content: React application serving correctly

2. **Python Flask API** - http://18.232.114.213/
   - Status: ✅ Fully functional
   - Endpoints: `/` and `/api/health` both working

### ⚠️ Deployments with Issues

3. **Nginx Static Demo** - http://18.215.255.226/
   - Status: ❌ Nginx default page detected
   - Issue: Application files deployed but nginx serving default page
   - Fix needed: Remove default server block from nginx.conf

4. **Node.js Application** - http://3.95.21.139:3000/
   - Status: ❌ Connection timeout
   - Issue: Service may not be running or port not accessible
   - Fix needed: Check PM2 process and port configuration

## Nginx Default Page Issue

### Problem Description
When deployments show "Welcome to nginx" instead of the actual application, it means:
- Application files are successfully deployed
- Nginx is running but serving the default page
- The default server block is taking precedence over the application configuration

### Root Cause
The default nginx server block in `/etc/nginx/nginx.conf` (Amazon Linux) or `/etc/nginx/sites-enabled/default` (Ubuntu) is configured to serve before the application-specific configuration.

### Solution
The nginx configurator has been updated to **completely remove** the default server block instead of just commenting it out. This ensures the application-specific configuration takes precedence.

### Manual Fix Process
If automatic fixes fail, use the troubleshooting tools:

1. Navigate to the appropriate troubleshooting directory
2. Use the existing SSH key setup
3. Apply the nginx configuration fix manually

## Monitoring Workflow

### Daily Monitoring
1. Run `./monitor-all-deployments.sh` for real-time monitoring
2. Press `v` to verify endpoints when deployments complete
3. Address any nginx default page issues immediately

### Quick Health Checks
```bash
# Fast endpoint verification
python3 quick-endpoint-check.py

# Comprehensive verification with fixes
python3 verify-all-endpoints.py --fix-nginx
```

### GitHub Actions Integration
The monitoring tools integrate with GitHub Actions to:
- Track deployment status in real-time
- Verify endpoints after successful deployments
- Detect configuration issues automatically
- Provide actionable fix recommendations

## Best Practices

### For Developers
1. Always verify endpoints after deployment
2. Check for nginx default page issues immediately
3. Use the monitoring tools to track deployment health
4. Address configuration issues before they affect users

### For Operations
1. Run monitoring during deployment windows
2. Keep the quick-endpoint-check.py running regularly
3. Maintain SSH access for manual fixes when needed
4. Monitor GitHub Actions workflow success rates

## Troubleshooting

### Common Issues

**Nginx Default Page:**
- Symptom: "Welcome to nginx" instead of application
- Cause: Default server block taking precedence
- Fix: Use nginx configurator fix or manual removal

**Connection Timeouts:**
- Symptom: Cannot connect to endpoint
- Cause: Service not running or port blocked
- Fix: Check service status and firewall rules

**Wrong Content:**
- Symptom: HTTP 200 but unexpected content
- Cause: Application serving wrong files
- Fix: Check document root and file permissions

### Emergency Procedures
1. Use `quick-endpoint-check.py` for immediate status
2. Check GitHub Actions logs for deployment errors
3. Use troubleshooting tools for manual intervention
4. Apply nginx fixes via the enhanced configurator

## Files and Scripts

### Main Tools
- `monitor-all-deployments.sh` - Interactive monitoring dashboard
- `quick-endpoint-check.py` - Fast endpoint verification
- `verify-all-endpoints.py` - Comprehensive verification with fixes
- `test-all-deployments.py` - Original test script (still functional)

### Configuration Files
- `workflows/app_configurators/nginx_configurator.py` - Enhanced with complete default server block removal
- `.github/workflows/deploy-generic-reusable.yml` - Updated nginx verification logic

### Troubleshooting Tools
- `troubleshooting-tools/` - Directory with SSH-enabled manual fix tools
- `fix-nginx-verification.py` - Nginx-specific troubleshooting
- `final-python-fix.py` - Python deployment troubleshooting

## Summary

The monitoring and verification system now provides:
- ✅ Real-time deployment monitoring
- ✅ Automatic nginx default page detection
- ✅ Interactive fix recommendations
- ✅ Comprehensive endpoint verification
- ✅ Integration with existing troubleshooting tools

All deployments are tracked and verified automatically, with clear indicators when manual intervention is needed.