# Node.js Application Debug Guide

## Overview
This guide explains how to use the debug and fix scripts for Node.js applications deployed on AWS Lightsail, including React + Node.js applications like the Instagram clone.

## Scripts

### 🆕 React + Node.js Specific Scripts

#### quick-check.py - Instant Status Check
**Use when**: You need immediate status of your React + Node.js deployment
```bash
python3 quick-check.py
```
- ⚡ Fast 30-second check
- ✅ Shows what's working/broken  
- 🎯 Provides specific next steps
- 🌐 Tests external connectivity
- Perfect for Instagram clone and similar React apps

#### debug-react-nodejs.py - Comprehensive React + Node.js Diagnostics
**Use when**: You need detailed analysis of React + Node.js issues
```bash
python3 debug-react-nodejs.py
```
- 🔍 Deep system analysis for React apps
- 📋 Checks React build, Node.js server, PM2, Nginx proxy
- 🌐 Tests all API endpoints
- 📊 Provides troubleshooting recommendations
- Specifically designed for React apps served by Node.js

#### fix-react-nodejs.py - Automated React + Node.js Fix
**Use when**: You want to automatically resolve React + Node.js issues
```bash
python3 fix-react-nodejs.py
```
- 🔧 Automated problem resolution
- 🏗️ Rebuilds React application (`npm run build`)
- 🖥️ Restarts Node.js server with PM2
- 🌐 Reconfigures Nginx proxy for Node.js
- Perfect for fixing Instagram clone deployment issues

### General Node.js Scripts

#### debug-nodejs.py
Comprehensive diagnostic tool that checks:
- Node.js and npm installation and versions
- Application directory structure
- package.json configuration
- Node modules installation status
- Application process status
- Port availability (default: 3000)
- PM2 process manager status
- Application logs
- File permissions
- Network connectivity

### fix-nodejs.py
Automated repair tool that:
- Installs Node.js and npm if missing
- Creates application directory structure
- Installs dependencies from package.json
- Fixes file permissions and ownership
- Configures PM2 process manager
- Starts/restarts the application
- Sets up PM2 to start on boot

## Usage

### Running Debug Script
```bash
# Basic usage
sudo python3 debug-nodejs.py

# Specify custom app directory
sudo python3 debug-nodejs.py --app-dir /var/www/myapp

# Specify custom port
sudo python3 debug-nodejs.py --port 8080

# Custom app directory and port
sudo python3 debug-nodejs.py --app-dir /var/www/myapp --port 8080
```

### Running Fix Script
```bash
# Source AWS credentials first
source .aws-creds.sh

# Run fix script interactively
python3 debug-scripts/fix-nodejs.py

# When prompted:
Instance name [nodejs-app-demo]: nodejs-demo-app-v2
AWS region [us-east-1]: us-east-1
Reboot instance after fix? (y/N): n

# Or provide inputs automatically
echo -e "nodejs-demo-app-v2\nus-east-1\nn" | python3 debug-scripts/fix-nodejs.py

# With reboot (recommended if PM2 not starting)
echo -e "nodejs-demo-app-v2\nus-east-1\ny" | python3 debug-scripts/fix-nodejs.py
```

**Note:** The script auto-detects your application directory by searching common locations:
- `/opt/nodejs-app`
- `/var/www/nodejs-app`
- `/opt/app`
- `/var/www/app`

**Reboot Option:** Answer 'y' to reboot after fixes. Useful for ensuring PM2 auto-starts on boot. See the Reboot Feature section below for details.

## What Gets Checked

### 1. Node.js Installation
- Verifies Node.js is installed
- Checks Node.js version
- Verifies npm is installed
- Checks npm version

### 2. Application Structure
- Checks if app directory exists
- Verifies package.json exists
- Validates package.json syntax
- Checks for node_modules directory

### 3. Dependencies
- Verifies node_modules are installed
- Checks if dependencies match package.json
- Identifies missing packages

### 4. Application Process
- Checks if app is running
- Verifies correct port binding
- Checks PM2 process status
- Validates process health

### 5. File Permissions
- Checks directory ownership
- Verifies file permissions
- Ensures ubuntu user has access

### 6. Network & Logs
- Tests port availability
- Checks application logs
- Verifies PM2 logs
- Tests localhost connectivity

## Common Issues Fixed

### Issue 1: Node.js Not Installed
**Symptom:** Command 'node' not found
**Fix:** Installs Node.js LTS version via NodeSource repository

### Issue 2: Dependencies Not Installed
**Symptom:** Cannot find module errors
**Fix:** Runs `npm install` to install all dependencies

### Issue 3: Wrong Permissions
**Symptom:** EACCES permission denied errors
**Fix:** Sets correct ownership to ubuntu:ubuntu and proper permissions

### Issue 4: Application Not Running
**Symptom:** Cannot connect to application
**Fix:** Starts application using PM2 with proper configuration

### Issue 5: PM2 Not Configured
**Symptom:** App doesn't restart after reboot
**Fix:** Configures PM2 startup script and saves process list

### Issue 6: Port Already in Use
**Symptom:** EADDRINUSE error
**Fix:** Identifies and stops conflicting processes

## Expected Output

### Successful Debug Output
```
=== Node.js Application Debug Report ===
✓ Node.js is installed (v18.x.x)
✓ npm is installed (v9.x.x)
✓ Application directory exists
✓ package.json is valid
✓ Dependencies are installed
✓ Application is running (PID: 12345)
✓ Port 3000 is available
✓ PM2 is managing the process
✓ File permissions are correct
✓ Application is accessible

All checks passed!
```

### Successful Fix Output
```
=== Node.js Application Fix Report ===
✓ Node.js installation verified
✓ Application directory created
✓ Dependencies installed
✓ File permissions fixed
✓ PM2 configured
✓ Application started successfully
✓ PM2 startup configured

Application is now running on port 3000
```

## Troubleshooting

### Script Fails to Run
- Ensure you're using `sudo`
- Check Python 3 is installed: `python3 --version`
- Verify script has execute permissions: `chmod +x debug-nodejs.py`

### Application Still Not Working After Fix
1. Check application logs: `pm2 logs`
2. Verify package.json has correct start script
3. Check for syntax errors in app.js
4. Ensure all environment variables are set
5. Verify database connections if applicable

### PM2 Issues
- Check PM2 status: `pm2 status`
- View PM2 logs: `pm2 logs`
- Restart PM2: `pm2 restart all`
- Reset PM2: `pm2 kill && pm2 resurrect`

## Manual Verification

After running the scripts, verify manually:

```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# Check if app is running
pm2 status

# View application logs
pm2 logs

# Test application
curl http://localhost:3000

# Check port usage
sudo netstat -tlnp | grep :3000
```

## Integration with Deployment

These scripts are designed to work with the GitHub Actions deployment workflow:
- Debug script runs automatically after deployment
- Fix script can be triggered manually if issues are detected
- Both scripts provide detailed output for troubleshooting

## Reboot Feature

The fix script includes an optional reboot feature for restarting the instance after applying fixes.

### When to Use Reboot

**✅ Use Reboot When:**
- PM2 won't start properly
- Processes are stuck or unresponsive
- After fixing multiple issues
- Testing auto-start configuration
- High memory usage or leaks
- Network connectivity issues

**❌ Skip Reboot When:**
- Simple permission fixes
- Production instances with active users
- Quick testing iterations
- Services are already working fine

### What Happens During Reboot

1. **Fix script completes** - All fixes applied successfully
2. **Reboot initiated** - Uses AWS Lightsail API (graceful shutdown)
3. **Instance restarts** - ~1-2 minutes total downtime
4. **Services auto-start** - PM2 processes start automatically
5. **Application ready** - App accessible on configured port

### What Persists After Reboot

**✅ Preserved:**
- All file changes and configurations
- Installed packages and dependencies
- PM2 saved processes (auto-start on boot)
- User data and application code

**❌ Reset:**
- Active connections
- Temporary files in /tmp
- Memory state
- Unsaved PM2 processes (use `pm2 save` first)

### Reboot Examples

```bash
# Without reboot
echo -e "nodejs-demo-app-v2\nus-east-1\nn" | python3 debug-scripts/nodejs/fix-nodejs.py

# With reboot (recommended for PM2 auto-start issues)
echo -e "nodejs-demo-app-v2\nus-east-1\ny" | python3 debug-scripts/nodejs/fix-nodejs.py
```

### Troubleshooting Reboot Issues

If instance won't come back after reboot:
```bash
# Check instance status
aws lightsail get-instance --instance-name <name> --region us-east-1

# Force stop/start if needed
aws lightsail stop-instance --instance-name <name> --region us-east-1
aws lightsail start-instance --instance-name <name> --region us-east-1
```

If PM2 doesn't auto-start after reboot:
```bash
# Configure PM2 startup
pm2 startup
pm2 save

# Verify startup is configured
systemctl status pm2-ubuntu
```

## Additional Resources

- [Node.js Documentation](https://nodejs.org/docs/)
- [npm Documentation](https://docs.npmjs.com/)
- [PM2 Documentation](https://pm2.keymetrics.io/docs/)
- [Express.js Guide](https://expressjs.com/en/guide/routing.html)
