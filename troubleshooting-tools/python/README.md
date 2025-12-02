# Python Application Debug Guide

## Overview
This guide explains how to use the debug and fix scripts for Python Flask applications deployed on AWS Lightsail.

## Scripts

### debug-python.py
Comprehensive diagnostic tool that checks:
- Python 3 installation and version
- pip installation and version
- Virtual environment setup
- Application directory structure
- requirements.txt presence
- Installed packages vs requirements
- Flask application status
- Gunicorn process status
- Port availability (default: 5000)
- Nginx configuration and status
- File permissions
- Application logs

### fix-python.py
Automated repair tool that:
- Installs Python 3 and pip if missing
- Creates virtual environment
- Installs all requirements
- Fixes file permissions and ownership
- Configures Gunicorn service
- Sets up Nginx reverse proxy
- Starts/restarts all services
- Enables services on boot

## Usage

### Running Debug Script
```bash
# Basic usage
sudo python3 debug-python.py

# Specify custom app directory
sudo python3 debug-python.py --app-dir /var/www/myapp

# Specify custom port
sudo python3 debug-python.py --port 8000

# Custom app directory and port
sudo python3 debug-python.py --app-dir /var/www/myapp --port 8000
```

### Running Fix Script
```bash
# Source AWS credentials first
source .aws-creds.sh

# Run fix script interactively
python3 debug-scripts/fix-python.py

# When prompted:
Instance name [python-app-demo]: python-flask-api-v2
AWS region [us-east-1]: us-east-1
Reboot instance after fix? (y/N): n

# Or provide inputs automatically
echo -e "python-flask-api-v2\nus-east-1\nn" | python3 debug-scripts/fix-python.py

# With reboot (recommended if Gunicorn won't start)
echo -e "python-flask-api-v2\nus-east-1\ny" | python3 debug-scripts/fix-python.py
```

**Note:** The script auto-detects your application directory by searching common locations:
- `/opt/python-app`
- `/var/www/python-app`
- `/opt/app`
- `/var/www/app`

**Reboot Option:** Answer 'y' to reboot after fixes. Useful for clearing dpkg locks or ensuring Gunicorn auto-starts. See the Reboot Feature section below for details.

## What Gets Checked

### 1. Python Environment
- Verifies Python 3 is installed
- Checks Python version
- Verifies pip is installed
- Checks pip version
- Validates virtual environment

### 2. Application Structure
- Checks if app directory exists
- Verifies app.py exists
- Checks for requirements.txt
- Validates Flask installation
- Checks for static/templates directories

### 3. Dependencies
- Verifies virtual environment packages
- Compares installed vs required packages
- Identifies missing dependencies
- Checks for version conflicts

### 4. Application Process
- Checks if Gunicorn is running
- Verifies correct port binding
- Validates worker processes
- Checks process health

### 5. Web Server
- Verifies Nginx is installed
- Checks Nginx configuration
- Validates reverse proxy setup
- Tests Nginx status

### 6. File Permissions
- Checks directory ownership
- Verifies file permissions
- Ensures ubuntu user has access
- Validates socket permissions

### 7. Logs & Connectivity
- Checks application logs
- Verifies Gunicorn logs
- Tests port availability
- Validates localhost connectivity

## Common Issues Fixed

### Issue 1: Python Not Installed
**Symptom:** Command 'python3' not found
**Fix:** Installs Python 3 and pip via apt

### Issue 2: Virtual Environment Missing
**Symptom:** No venv directory found
**Fix:** Creates virtual environment and installs all requirements

### Issue 3: Dependencies Not Installed
**Symptom:** ModuleNotFoundError
**Fix:** Activates venv and runs `pip install -r requirements.txt`

### Issue 4: Wrong Permissions
**Symptom:** Permission denied errors
**Fix:** Sets correct ownership to ubuntu:ubuntu and proper permissions

### Issue 5: Gunicorn Not Running
**Symptom:** Cannot connect to application
**Fix:** Creates systemd service and starts Gunicorn

### Issue 6: Nginx Not Configured
**Symptom:** 502 Bad Gateway
**Fix:** Creates Nginx config with reverse proxy to Gunicorn

### Issue 7: Services Not Enabled
**Symptom:** App doesn't start after reboot
**Fix:** Enables Gunicorn and Nginx services on boot

## Expected Output

### Successful Debug Output
```
=== Python Application Debug Report ===
✓ Python 3 is installed (v3.x.x)
✓ pip is installed (v23.x.x)
✓ Virtual environment exists
✓ Application directory exists
✓ requirements.txt found
✓ All dependencies installed
✓ Flask is installed
✓ Gunicorn is running (PID: 12345)
✓ Port 5000 is available
✓ Nginx is running
✓ Nginx configuration is valid
✓ File permissions are correct
✓ Application is accessible

All checks passed!
```

### Successful Fix Output
```
=== Python Application Fix Report ===
✓ Python installation verified
✓ Virtual environment created
✓ Dependencies installed
✓ File permissions fixed
✓ Gunicorn service configured
✓ Nginx configured
✓ Services started successfully
✓ Services enabled on boot

Application is now running on port 5000
Access via: http://your-instance-ip
```

## Troubleshooting

### Script Fails to Run
- Ensure you're using `sudo`
- Check Python 3 is installed: `python3 --version`
- Verify script has execute permissions: `chmod +x debug-python.py`

### Application Still Not Working After Fix
1. Check Gunicorn logs: `sudo journalctl -u gunicorn -n 50`
2. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Verify app.py has no syntax errors: `python3 app.py`
4. Check virtual environment activation
5. Ensure all environment variables are set

### Gunicorn Issues
- Check service status: `sudo systemctl status gunicorn`
- View logs: `sudo journalctl -u gunicorn -f`
- Restart service: `sudo systemctl restart gunicorn`
- Check socket: `ls -la /var/www/python-app/gunicorn.sock`

### Nginx Issues
- Check configuration: `sudo nginx -t`
- View error logs: `sudo tail -f /var/log/nginx/error.log`
- Restart Nginx: `sudo systemctl restart nginx`
- Check if port 80 is open: `sudo netstat -tlnp | grep :80`

## Manual Verification

After running the scripts, verify manually:

```bash
# Check Python version
python3 --version

# Check pip version
pip3 --version

# Activate virtual environment
source /var/www/python-app/venv/bin/activate

# Check installed packages
pip list

# Check Gunicorn status
sudo systemctl status gunicorn

# Check Nginx status
sudo systemctl status nginx

# Test application locally
curl http://localhost:5000

# Test via Nginx
curl http://localhost

# Check port usage
sudo netstat -tlnp | grep :5000
```

## Service Management

### Gunicorn Service
```bash
# Start service
sudo systemctl start gunicorn

# Stop service
sudo systemctl stop gunicorn

# Restart service
sudo systemctl restart gunicorn

# View logs
sudo journalctl -u gunicorn -f

# Check status
sudo systemctl status gunicorn
```

### Nginx Service
```bash
# Start Nginx
sudo systemctl start nginx

# Stop Nginx
sudo systemctl stop nginx

# Restart Nginx
sudo systemctl restart nginx

# Reload configuration
sudo systemctl reload nginx

# Test configuration
sudo nginx -t
```

## Integration with Deployment

These scripts are designed to work with the GitHub Actions deployment workflow:
- Debug script runs automatically after deployment
- Fix script can be triggered manually if issues are detected
- Both scripts provide detailed output for troubleshooting
- Logs are captured for CI/CD pipeline analysis

## Reboot Feature

The fix script includes an optional reboot feature for restarting the instance after applying fixes.

### When to Use Reboot

**✅ Use Reboot When:**
- Gunicorn won't start properly
- Services are stuck or unresponsive
- After fixing multiple issues
- Clearing dpkg/apt locks
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
4. **Services auto-start** - Gunicorn and Nginx start automatically
5. **Application ready** - Flask app accessible

### What Persists After Reboot

**✅ Preserved:**
- All file changes and configurations
- Installed packages and virtual environment
- Systemd enabled services (auto-start on boot)
- User data and application code

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

If Gunicorn doesn't auto-start after reboot:
```bash
# Enable Gunicorn on boot
sudo systemctl enable gunicorn

# Verify it's enabled
systemctl is-enabled gunicorn
```

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
