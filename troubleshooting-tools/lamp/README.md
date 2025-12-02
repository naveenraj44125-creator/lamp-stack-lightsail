# LAMP Stack Debug & Fix Scripts

## debug-lamp.py

**Purpose**: Comprehensive diagnostic tool for LAMP stack (Apache + PHP + MySQL) deployments on AWS Lightsail Ubuntu instances.

### What It Does

This script connects to your Lightsail instance via SSH and performs 10 diagnostic checks:

#### 1. Apache Service Status
- Checks if Apache2 is running
- Shows service state, uptime, and process information
- Identifies if Apache failed to start

#### 2. PHP Version Check
- Verifies PHP is installed
- Shows PHP version (e.g., PHP 8.5.0)
- Confirms PHP CLI is accessible

#### 3. MySQL/MariaDB Status
- Checks if database service is running
- Shows service state (may not exist if using external RDS)
- Identifies database connectivity issues

#### 4. File Structure Analysis
- Lists all files in `/var/www/html` recursively
- Shows directory structure (config, css, logs, tmp)
- Identifies missing or misplaced files

#### 5. Apache Configuration
- Displays VirtualHost configuration
- Shows DocumentRoot and ServerRoot
- Lists enabled modules and settings

#### 6. Apache Error Log
- Shows last 20 lines of error log
- Identifies recent errors or warnings
- Helps diagnose Apache startup issues

#### 7. Apache Access Log
- Shows last 10 access log entries
- Identifies recent HTTP requests
- Shows response codes and user agents

#### 8. PHP Functionality Test
- Executes PHP code to verify it works
- Confirms PHP can execute scripts
- Shows PHP version via code execution

#### 9. PHP Modules
- Lists installed PHP extensions
- Shows first 20 modules (Core, date, json, etc.)
- Identifies missing required modules

#### 10. Local HTTP Test
- Performs curl request to localhost
- Shows HTTP response headers
- Verifies Apache is serving content

### Usage

```bash
# Source AWS credentials first
source .aws-creds.sh

# Run debug script
./debug-scripts/debug-lamp.py

# When prompted:
Instance name [lamp-stack-demo]: lamp-stack-demo-v2
AWS region [us-east-1]: us-east-1
```

### Example Output

```
🔍 Debugging LAMP Stack Deployment
================================================================================
📡 Sending command to ubuntu@3.90.150.41:

📋 1. Checking Apache status:
● apache2.service - The Apache HTTP Server
     Active: active (running) since Tue 2025-12-02 16:04:25 UTC
     ✅ Apache is running

📋 2. Checking PHP version:
PHP 8.5.0 (cli)
     ✅ PHP is installed and working

📋 10. Testing local curl:
HTTP/1.1 200 OK
     ✅ Application is responding

✅ Debug complete
```

### Common Issues Detected

| Issue | Symptom in Output | Next Step |
|-------|------------------|-----------|
| Apache not running | `Active: inactive (dead)` | Run `fix-lamp.py` |
| PHP not installed | `php: command not found` | Check deployment logs |
| Permission errors | `Permission denied` in logs | Run `fix-lamp.py` |
| Missing files | Empty `/var/www/html` | Re-run deployment |
| 403 Forbidden | `403` in access log | Run `fix-lamp.py` |

---

## fix-lamp.py

**Purpose**: Automated repair tool for common LAMP stack deployment issues.

### What It Does

This script fixes the most common LAMP deployment problems:

#### 1. Fix Ownership
- Changes all files to `www-data:www-data`
- Ensures Apache can read application files
- Fixes "Permission denied" errors

#### 2. Fix Directory Permissions
- Sets all directories to `755` (rwxr-xr-x)
- Allows Apache to traverse directories
- Enables directory listing if configured

#### 3. Fix File Permissions
- Sets all files to `644` (rw-r--r--)
- Allows Apache to read files
- Prevents execution of non-executable files

#### 4. Enable Apache Modules
- Enables `mod_rewrite` for URL rewriting
- Required for many PHP frameworks
- Skips if already enabled

#### 5. Test Configuration
- Runs `apache2ctl configtest`
- Validates Apache configuration syntax
- Prevents restart with broken config

#### 6. Restart Apache
- Performs full Apache restart
- Applies all configuration changes
- Clears any stuck processes

#### 7. Verify Permissions
- Lists files to confirm changes
- Shows new ownership and permissions
- Validates fix was applied

#### 8. Test HTTP Access
- Performs local curl test
- Verifies Apache is serving content
- Confirms fix resolved issues

### Usage

```bash
# Source AWS credentials first
source .aws-creds.sh

# Run fix script interactively
python3 debug-scripts/fix-lamp.py

# When prompted:
Instance name [lamp-stack-demo]: lamp-stack-demo-v2
AWS region [us-east-1]: us-east-1
Reboot instance after fix? (y/N): n

# Or provide inputs automatically (no reboot)
echo -e "lamp-stack-demo-v2\nus-east-1\nn" | python3 debug-scripts/fix-lamp.py

# With reboot (recommended for stuck services or major fixes)
echo -e "lamp-stack-demo-v2\nus-east-1\ny" | python3 debug-scripts/fix-lamp.py
```

### Reboot Option

The fix script includes an optional reboot feature:

**When to reboot (answer 'y'):**
- Apache won't restart properly
- Services are stuck or unresponsive
- After fixing multiple issues
- To test auto-start configuration
- Clearing dpkg/apt locks

**When NOT to reboot (answer 'n'):**
- Simple permission fixes
- Production instances with active users
- Quick testing iterations
- Services are already working

**What happens during reboot:**
- Graceful shutdown (~30 seconds)
- Instance restarts (~60 seconds)
- Services auto-start (~30 seconds)
- Total downtime: ~1-2 minutes

**What persists after reboot:**
- ✅ All file changes and configurations
- ✅ Installed packages (Apache, PHP, MySQL)
- ✅ Systemd enabled services (auto-start on boot)
- ✅ User data and application code

**What resets:**
- ❌ Active connections
- ❌ Temporary files in /tmp
- ❌ Memory state
- ❌ Unsaved configurations

### Troubleshooting Reboot Issues

If instance won't come back after reboot:
```bash
# Check instance status
aws lightsail get-instance --instance-name <name> --region us-east-1

# Force stop/start if needed
aws lightsail stop-instance --instance-name <name> --region us-east-1
aws lightsail start-instance --instance-name <name> --region us-east-1
```

If Apache doesn't auto-start after reboot:
```bash
# Enable Apache on boot
sudo systemctl enable apache2

# Verify it's enabled
systemctl is-enabled apache2
```

### Example Output

```
🔧 Fixing LAMP Stack Deployment Issues
================================================================================

🔧 1. Fixing ownership...
✅ Set ownership to www-data:www-data

🔧 2. Fixing directory permissions...
✅ Set directory permissions to 755

🔧 3. Fixing file permissions...
✅ Set file permissions to 644

🔧 6. Restarting Apache...
✅ Apache restarted

🧪 Testing local access:
HTTP/1.1 200 OK
✅ Application is responding

✅ LAMP stack deployment fixed successfully
```

### When to Use

Run this script when you encounter:
- ✅ 403 Forbidden errors
- ✅ "Permission denied" in logs
- ✅ Apache not serving PHP files
- ✅ Files uploaded manually via SCP/SFTP
- ✅ After deployment failures
- ✅ After manual file modifications

### What It Doesn't Fix

This script cannot fix:
- ❌ PHP syntax errors in your code
- ❌ Missing PHP extensions
- ❌ Database connection issues
- ❌ Apache not installed
- ❌ Broken Apache configuration files

For these issues, check deployment logs or run `debug-lamp.py` for more information.

---

## Workflow

```
Deployment Issue
       ↓
Run debug-lamp.py
       ↓
Review diagnostic output
       ↓
Run fix-lamp.py
       ↓
Re-run debug-lamp.py to verify
       ↓
Issue resolved ✅
```

## Prerequisites

- AWS credentials configured (`.aws-creds.sh`)
- Python 3 with boto3 installed
- SSH access to Lightsail instance
- Instance running Ubuntu OS
