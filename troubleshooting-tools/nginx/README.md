# Nginx Static Site Debug & Fix Scripts

## debug-nginx.py

**Purpose**: Comprehensive diagnostic tool for Nginx static site deployments on AWS Lightsail Ubuntu instances.

### What It Does

This script connects to your Lightsail instance via SSH and performs 10 diagnostic checks:

#### 1. File Structure Check
- Lists all files in `/var/www/html` recursively
- Shows directory structure (assets/css, assets/js, config, logs, tmp)
- Identifies missing or misplaced files
- Displays file sizes and permissions

#### 2. HTML Files Discovery
- Searches for all `.html` files in `/var/www`
- Shows file paths and sizes
- Confirms index.html exists
- Identifies orphaned HTML files

#### 3. Nginx Configuration
- Displays active site configuration
- Shows server blocks and location rules
- Lists security headers
- Identifies caching rules

#### 4. Nginx Config Test
- Runs `nginx -t` to validate syntax
- Checks for configuration errors
- Prevents reload with broken config

#### 5. Nginx Service Status
- Shows systemd service state
- Displays uptime and process information
- Identifies if Nginx failed to start
- Shows worker processes

#### 6. Nginx Error Log
- Shows last 20 lines of error log
- Identifies 404 errors for missing files
- Shows permission denied errors
- Displays recent error patterns

#### 7. Nginx Access Log
- Shows last 10 access log entries
- Displays HTTP status codes
- Shows client IPs and user agents
- Identifies attack attempts (Struts exploits, etc.)

#### 8. File Permissions
- Lists files with ownership details
- Shows permission bits (rwxr-xr-x)
- Identifies incorrect ownership
- Displays file sizes

#### 9. Recent Deployments
- Lists deployment packages in `/tmp`
- Shows `.tar.gz` files with timestamps
- Identifies if deployment package exists
- Helps track deployment history

#### 10. Local HTTP Test
- Performs curl request to localhost
- Shows HTTP response headers
- Verifies Nginx is serving content
- Confirms HTTP 200 status

### Usage

```bash
# Source AWS credentials first
source .aws-creds.sh

# Run debug script
./debug-scripts/debug-nginx.py

# When prompted:
Instance name [nginx-static-demo]: nginx-static-demo-v2
AWS region [us-east-1]: us-east-1
```

### Example Output

```
🔍 Debugging Nginx Deployment
================================================================================
📡 Sending command to ubuntu@52.203.169.26:

📋 1. Checking /var/www/html structure:
drwxr-xr-x 6 www-data www-data 4096 Dec  2 15:57 .
-rw-r--r-- 1 www-data www-data 4930 Dec  2 15:57 index.html
drwxr-xr-x 4 www-data www-data 4096 Dec  1 01:09 assets
     ✅ Files deployed correctly

📋 5. Checking nginx service status:
Active: active (running) since Tue 2025-12-02 15:57:51 UTC
     ✅ Nginx is running

📋 10. Testing local curl:
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
     ✅ Site is accessible

✅ Debug complete
```

### Common Issues Detected

| Issue | Symptom in Output | Next Step |
|-------|------------------|-----------|
| Nginx not running | `Active: inactive (dead)` | Check deployment logs |
| Missing index.html | `No HTML files found` | Re-run deployment |
| Permission errors | `403` in error log | Run `fix-nginx.py` |
| Wrong ownership | Files owned by `ubuntu` | Run `fix-nginx.py` |
| Config errors | `nginx -t` fails | Check nginx config |
| 404 errors | Many 404s in error log | Check file paths |

---

## fix-nginx.py

**Purpose**: Automated repair tool for common Nginx static site deployment issues.

### What It Does

This script fixes the most common Nginx deployment problems:

#### 1. Fix Ownership
- Changes all files to `www-data:www-data`
- Ensures Nginx can read static files
- Fixes "Permission denied" errors
- Applies recursively to all subdirectories

#### 2. Fix Directory Permissions
- Sets all directories to `755` (rwxr-xr-x)
- Allows Nginx to traverse directories
- Enables directory access
- Applies to assets/, css/, js/ folders

#### 3. Fix File Permissions
- Sets all files to `644` (rw-r--r--)
- Allows Nginx to read HTML, CSS, JS files
- Prevents execution of static files
- Applies to all file types

#### 4. Test Configuration
- Runs `nginx -t` to validate syntax
- Checks for configuration errors
- Prevents reload with broken config
- Shows configuration file paths

#### 5. Reload Nginx
- Performs graceful reload
- Applies permission changes
- Doesn't drop connections
- Faster than full restart

#### 6. Verify Permissions
- Lists files to confirm changes
- Shows new ownership (www-data)
- Displays new permissions (755/644)
- Validates fix was applied

#### 7. Test HTTP Access
- Performs local curl test
- Shows HTTP response headers
- Verifies Nginx is serving content
- Confirms 200 OK status

### Usage

```bash
# Source AWS credentials first
source .aws-creds.sh

# Run fix script interactively
python3 debug-scripts/fix-nginx.py

# When prompted:
Instance name [nginx-static-demo]: nginx-static-demo-v2
AWS region [us-east-1]: us-east-1
Reboot instance after fix? (y/N): n

# Or provide inputs automatically
echo -e "nginx-static-demo-v2\nus-east-1\nn" | python3 debug-scripts/fix-nginx.py

# With reboot option
echo -e "nginx-static-demo-v2\nus-east-1\ny" | python3 debug-scripts/fix-nginx.py
```

**Reboot Option:** Answer 'y' to reboot after fixes. Useful for stuck services or testing auto-start. See the Reboot Feature section below for details.

### Example Output

```
🔧 Fixing Nginx Deployment Issues
================================================================================

🔧 1. Fixing ownership...
✅ Set ownership to www-data:www-data

🔧 2. Fixing directory permissions...
✅ Set directory permissions to 755

🔧 3. Fixing file permissions...
✅ Set file permissions to 644

🔧 4. Testing nginx configuration...
nginx: configuration file /etc/nginx/nginx.conf test is successful

🔧 5. Reloading nginx...
✅ Nginx reloaded

📋 Current permissions:
drwxr-xr-x 6 www-data www-data 4096 index.html
     ✅ Permissions fixed

🧪 Testing local access:
HTTP/1.1 200 OK
     ✅ Site is accessible

✅ Nginx deployment fixed successfully
```

### When to Use

Run this script when you encounter:
- ✅ **403 Forbidden errors** - Most common issue
- ✅ **Permission denied in logs** - File access issues
- ✅ **Files uploaded via SCP/SFTP** - Wrong ownership
- ✅ **After manual file modifications** - Permissions changed
- ✅ **After deployment failures** - Incomplete deployment
- ✅ **Nginx not serving files** - Access issues

### What It Fixes

| Problem | How It's Fixed |
|---------|---------------|
| 403 Forbidden | Sets files to 644, dirs to 755 |
| Wrong ownership | Changes to www-data:www-data |
| Permission denied | Fixes all file permissions |
| Nginx not reloading | Performs graceful reload |

### What It Doesn't Fix

This script cannot fix:
- ❌ **Missing files** - Re-run deployment
- ❌ **Nginx not installed** - Check deployment logs
- ❌ **Broken nginx config** - Manual config fix needed
- ❌ **Network/firewall issues** - Check AWS security groups
- ❌ **DNS problems** - Check domain configuration

### Troubleshooting

**Script fails to connect:**
```bash
# Verify instance exists and is running
aws lightsail get-instance --instance-name nginx-static-demo-v2 --region us-east-1

# Check instance state
aws lightsail get-instance-state --instance-name nginx-static-demo-v2 --region us-east-1
```

**Fix doesn't resolve issue:**
1. Run `debug-nginx.py` again to see what's still wrong
2. Check nginx error log for specific errors
3. Verify files were actually deployed
4. Check nginx configuration syntax

**Permission denied after fix:**
- Files may have been re-uploaded with wrong ownership
- Run fix script again
- Consider using deployment workflow instead of manual uploads

### Best Practices

1. ✅ **Run debug first** - Understand the problem before fixing
2. ✅ **Review output** - Don't blindly run fix
3. ✅ **Verify after fix** - Run debug again to confirm
4. ✅ **Check logs** - Error log shows specific issues
5. ✅ **Use deployment workflow** - Prevents permission issues

## Reboot Feature

The fix script includes an optional reboot feature for restarting the instance after applying fixes.

### When to Use Reboot

**✅ Use Reboot When:**
- Nginx won't restart properly
- Services are stuck or unresponsive
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
5. **Site ready** - Static site accessible

### What Persists After Reboot

**✅ Preserved:**
- All file changes and configurations
- Installed packages (Nginx)
- Systemd enabled services (auto-start on boot)
- User data and static files

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

### Quick Reference

```bash
# Full diagnostic workflow
source .aws-creds.sh
./debug-scripts/debug-nginx.py    # Diagnose
./debug-scripts/fix-nginx.py      # Fix
./debug-scripts/debug-nginx.py    # Verify
```
