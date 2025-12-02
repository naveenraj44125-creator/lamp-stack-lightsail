# React Application Debug Guide

## Overview
This guide explains how to use the debug and fix scripts for React applications deployed on AWS Lightsail.

## Scripts

### debug-react.py
Comprehensive diagnostic tool that checks:
- Node.js and npm installation and versions
- Application directory structure
- package.json configuration
- Node modules installation status
- Build directory existence
- Nginx installation and status
- Nginx configuration for React SPA
- Port availability (default: 80)
- File permissions
- Application accessibility
- Static file serving

### fix-react.py
Automated repair tool that:
- Installs Node.js and npm if missing
- Creates application directory structure
- Installs dependencies from package.json
- Builds production React application
- Installs and configures Nginx
- Sets up SPA routing (fallback to index.html)
- Fixes file permissions and ownership
- Starts/restarts Nginx service
- Enables Nginx on boot

## Usage

### Running Debug Script
```bash
# Basic usage
sudo python3 debug-react.py

# Specify custom app directory
sudo python3 debug-react.py --app-dir /var/www/myapp

# Specify custom port
sudo python3 debug-react.py --port 8080

# Custom app directory and port
sudo python3 debug-react.py --app-dir /var/www/myapp --port 8080
```

### Running Fix Script
```bash
# Source AWS credentials first
source .aws-creds.sh

# Run fix script interactively
python3 debug-scripts/fix-react.py

# When prompted:
Instance name [react-app-demo]: react-dashboard-v2
AWS region [us-east-1]: us-east-1
Reboot instance after fix? (y/N): n

# Or provide inputs automatically
echo -e "react-dashboard-v2\nus-east-1\nn" | python3 debug-scripts/fix-react.py

# With reboot (useful for Nginx configuration issues)
echo -e "react-dashboard-v2\nus-east-1\ny" | python3 debug-scripts/fix-react.py
```

**Reboot Option:** Answer 'y' to reboot after fixes. Useful for ensuring Nginx configuration is fully applied. See the Reboot Feature section below for details.

## What Gets Checked

### 1. Node.js Environment
- Verifies Node.js is installed
- Checks Node.js version
- Verifies npm is installed
- Checks npm version

### 2. Application Structure
- Checks if app directory exists
- Verifies package.json exists
- Validates package.json syntax
- Checks for node_modules directory
- Verifies build directory exists
- Checks for index.html in build

### 3. Dependencies
- Verifies node_modules are installed
- Checks if dependencies match package.json
- Identifies missing packages
- Validates React installation

### 4. Build Output
- Checks if production build exists
- Verifies build/index.html
- Checks for static assets
- Validates build structure

### 5. Web Server
- Verifies Nginx is installed
- Checks Nginx configuration
- Validates SPA routing setup
- Tests Nginx status
- Checks if Nginx is enabled

### 6. File Permissions
- Checks directory ownership
- Verifies file permissions
- Ensures www-data user has access
- Validates build directory permissions

### 7. Network & Accessibility
- Tests port availability
- Checks application accessibility
- Verifies static file serving
- Tests localhost connectivity

## Common Issues Fixed

### Issue 1: Node.js Not Installed
**Symptom:** Command 'node' not found
**Fix:** Installs Node.js LTS version via NodeSource repository

### Issue 2: Dependencies Not Installed
**Symptom:** Cannot find module errors during build
**Fix:** Runs `npm install` to install all dependencies

### Issue 3: Build Directory Missing
**Symptom:** 404 errors, no content served
**Fix:** Runs `npm run build` to create production build

### Issue 4: Nginx Not Installed
**Symptom:** Cannot connect to application
**Fix:** Installs Nginx via apt

### Issue 5: Wrong Nginx Configuration
**Symptom:** 404 on client-side routes, SPA routing broken
**Fix:** Creates proper Nginx config with try_files for SPA

### Issue 6: Wrong Permissions
**Symptom:** 403 Forbidden errors
**Fix:** Sets correct ownership to www-data:www-data and proper permissions

### Issue 7: Nginx Not Running
**Symptom:** Connection refused
**Fix:** Starts Nginx service and enables on boot

## Expected Output

### Successful Debug Output
```
=== React Application Debug Report ===
✓ Node.js is installed (v18.x.x)
✓ npm is installed (v9.x.x)
✓ Application directory exists
✓ package.json is valid
✓ Dependencies are installed
✓ Build directory exists
✓ index.html found in build
✓ Nginx is installed
✓ Nginx is running
✓ Nginx configuration is valid
✓ Port 80 is available
✓ File permissions are correct
✓ Application is accessible

All checks passed!
```

### Successful Fix Output
```
=== React Application Fix Report ===
✓ Node.js installation verified
✓ Application directory created
✓ Dependencies installed
✓ Production build created
✓ Nginx installed
✓ Nginx configured for SPA
✓ File permissions fixed
✓ Nginx started successfully
✓ Nginx enabled on boot

Application is now accessible on port 80
Access via: http://your-instance-ip
```

## Troubleshooting

### Script Fails to Run
- Ensure you're using `sudo`
- Check Python 3 is installed: `python3 --version`
- Verify script has execute permissions: `chmod +x debug-react.py`

### Application Still Not Working After Fix
1. Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
2. Check Nginx access logs: `sudo tail -f /var/log/nginx/access.log`
3. Verify build was successful: `ls -la /var/www/react-app/build`
4. Test Nginx config: `sudo nginx -t`
5. Check for JavaScript errors in browser console

### Build Issues
- Check Node.js version compatibility
- Verify all dependencies installed: `npm list`
- Check for build errors: `npm run build`
- Ensure enough disk space: `df -h`
- Clear npm cache: `npm cache clean --force`

### Nginx Issues
- Check configuration: `sudo nginx -t`
- View error logs: `sudo tail -f /var/log/nginx/error.log`
- Restart Nginx: `sudo systemctl restart nginx`
- Check if port 80 is open: `sudo netstat -tlnp | grep :80`

### SPA Routing Issues
- Verify Nginx config has `try_files $uri /index.html`
- Check browser console for 404 errors
- Test direct URL access to routes
- Ensure React Router is properly configured

## Manual Verification

After running the scripts, verify manually:

```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# Check if build exists
ls -la /var/www/react-app/build

# Check Nginx status
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t

# Test application locally
curl http://localhost

# Check port usage
sudo netstat -tlnp | grep :80

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Nginx Configuration Details

The fix script creates an Nginx configuration that:
- Serves static files from the build directory
- Implements SPA routing with `try_files`
- Sets proper cache headers for static assets
- Configures gzip compression
- Handles client-side routing correctly

Example configuration:
```nginx
server {
    listen 80;
    server_name _;
    root /var/www/react-app/build;
    index index.html;

    location / {
        try_files $uri /index.html;
    }

    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Service Management

### Nginx Service
```bash
# Start Nginx
sudo systemctl start nginx

# Stop Nginx
sudo systemctl stop nginx

# Restart Nginx
sudo systemctl restart nginx

# Reload configuration (no downtime)
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx

# Enable on boot
sudo systemctl enable nginx
```

## Rebuilding Application

If you need to rebuild the React app:

```bash
# Navigate to app directory
cd /var/www/react-app

# Install dependencies (if needed)
npm install

# Create production build
npm run build

# Restart Nginx
sudo systemctl restart nginx
```

## Integration with Deployment

These scripts are designed to work with the GitHub Actions deployment workflow:
- Debug script runs automatically after deployment
- Fix script can be triggered manually if issues are detected
- Both scripts provide detailed output for troubleshooting
- Build process is automated during deployment
- Nginx is automatically configured for SPA routing

## Reboot Feature

The fix script includes an optional reboot feature for restarting the instance after applying fixes.

### When to Use Reboot

**✅ Use Reboot When:**
- Nginx won't restart properly
- Configuration changes not taking effect
- After fixing multiple issues
- Testing auto-start configuration
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
4. **Services auto-start** - Nginx starts automatically
5. **Application ready** - React app accessible

### What Persists After Reboot

**✅ Preserved:**
- All file changes and configurations
- Installed packages (Node.js, Nginx)
- Production build files
- Systemd enabled services (auto-start on boot)
- Nginx configuration

**❌ Reset:**
- Active connections
- Temporary files in /tmp
- Memory state

### Troubleshooting Reboot Issues

If instance won't come back after reboot:
```bash
# Check instance status
aws lightsail get-instance --instance-name <name> --region us-east-1

# Force stop/start if needed
aws lightsail stop-instance --instance-name <name> --region us-east-1
aws lightsail start-instance --instance-name <name> --region us-east-1
```

If Nginx doesn't auto-start after reboot:
```bash
# Enable Nginx on boot
sudo systemctl enable nginx

# Verify it's enabled
systemctl is-enabled nginx
```

## Additional Resources

- [React Documentation](https://react.dev/)
- [Create React App Deployment](https://create-react-app.dev/docs/deployment/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [React Router Documentation](https://reactrouter.com/)
- [SPA Deployment Best Practices](https://create-react-app.dev/docs/deployment/#serving-apps-with-client-side-routing)
