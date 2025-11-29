# Deployment Issue Prevention Guide

This document outlines the preventive measures implemented to avoid common deployment issues.

## Preventive Measures Implemented

### 1. **Automatic dpkg Health Check** ✅
**Location:** `workflows/dependency_manager.py` - `install_all_dependencies()`

**What it does:**
- Checks dpkg state before any package installation
- Automatically runs `dpkg --configure -a` if broken state detected
- Fixes broken dependencies with `apt-get install -f -y`

**Prevents:**
- "dpkg was interrupted" errors
- Package installation failures due to broken dpkg state

```python
# Check if dpkg is in a broken state
if sudo dpkg --audit 2>&1 | grep -q "broken"; then
    sudo dpkg --configure -a
    sudo apt-get install -f -y
fi
```

---

### 2. **Retry Logic for Failed Installations** ✅
**Location:** `workflows/dependency_manager.py` - `_install_dependency()`

**What it does:**
- Retries failed dependency installations up to 2 times
- Fixes dpkg between retry attempts
- Continues with other dependencies even if one fails

**Prevents:**
- Transient network failures from blocking deployments
- Single package failure from stopping entire deployment

```python
max_retries = 2
for attempt in range(max_retries):
    if attempt > 0:
        # Fix dpkg before retry
        sudo dpkg --configure -a
    success = install_package()
    if success:
        break
```

---

### 3. **Pre-flight Health Check in Workflow** ✅
**Location:** `.github/workflows/deploy-generic-reusable.yml`

**What it does:**
- Runs before dependency installation starts
- Checks and fixes dpkg state
- Doesn't fail workflow if issues found (logs warning instead)

**Prevents:**
- Starting deployment on unhealthy instances
- Wasting time on deployments that will fail

```yaml
- name: Pre-flight Instance Health Check
  run: |
    # Check dpkg state
    # Fix if broken
    # Continue even if issues found
```

---

### 4. **System Health Check in Pre-deployment** ✅
**Location:** `workflows/deploy-pre-steps-generic.py` - `_system_health_check()`

**What it does:**
- Checks disk space
- Checks memory usage
- Checks dpkg state and fixes if needed
- Checks for apt locks
- Checks internet connectivity

**Prevents:**
- Deployments failing due to full disk
- Package installations failing due to locked apt
- Network-related failures

```bash
# Disk space check
df -h /

# Memory check
free -h

# dpkg check
dpkg --audit

# apt lock check
lsof /var/lib/dpkg/lock-frontend

# Connectivity check
ping -c 1 8.8.8.8
```

---

### 5. **PYTHONPATH Configuration** ✅
**Location:** `.github/workflows/deploy-generic-reusable.yml`

**What it does:**
- Sets `PYTHONPATH` to include workflows directory
- Ensures Python can import deployment modules

**Prevents:**
- `ModuleNotFoundError` for deployment scripts
- Import failures in GitHub Actions

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/workflows"
```

---

### 6. **Version-Specific Package Installation** ✅
**Location:** `workflows/dependency_manager.py` - `_install_python()`

**What it does:**
- Installs version-specific packages (e.g., `python3.10-venv`)
- Falls back to generic packages if specific version unavailable
- Handles Ubuntu version differences

**Prevents:**
- "package not found" errors
- Virtual environment creation failures

```python
if version == "3.10":
    sudo apt-get install -y python3 python3-pip python3-dev python3.10-venv
else:
    # Try specific version, fallback to python3
    sudo apt-get install -y python{version}-venv || sudo apt-get install -y python3-venv
```

---

## How These Measures Work Together

```
┌─────────────────────────────────────────────────────────┐
│ 1. Workflow Pre-flight Check                           │
│    ├─ Check dpkg state                                 │
│    ├─ Fix if broken                                    │
│    └─ Log warning if issues                            │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Pre-deployment System Health Check                  │
│    ├─ Check disk/memory/connectivity                   │
│    ├─ Check dpkg state again                           │
│    ├─ Check for apt locks                              │
│    └─ Fix any issues found                             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Dependency Installation with Retry                  │
│    ├─ Check dpkg before installations                  │
│    ├─ Install each dependency                          │
│    ├─ Retry failed installations (up to 2x)            │
│    ├─ Fix dpkg between retries                         │
│    └─ Continue with other deps if one fails            │
└─────────────────────────────────────────────────────────┘
```

---

## Testing the Preventive Measures

To verify these measures work, you can:

1. **Test dpkg fix:**
   ```bash
   # Simulate broken dpkg (don't do this in production!)
   sudo dpkg --configure -a
   # Then run deployment - it should auto-fix
   ```

2. **Test retry logic:**
   - Temporarily break a package name in config
   - Deployment should retry and log the failure
   - Other packages should still install

3. **Test health checks:**
   - Check workflow logs for "Pre-flight Health Check" step
   - Check deployment logs for "SYSTEM HEALTH CHECK" section

---

## What to Do If Issues Still Occur

### If dpkg is still broken:
```bash
# SSH into instance
ssh ubuntu@<instance-ip>

# Fix dpkg manually
sudo dpkg --configure -a
sudo apt-get update
sudo apt-get install -f -y

# Re-run deployment
```

### If apt is locked:
```bash
# Check what's locking apt
sudo lsof /var/lib/dpkg/lock-frontend

# Wait for process to finish or kill it
sudo kill <PID>

# Re-run deployment
```

### If instance is unresponsive:
```bash
# Reboot via AWS CLI or Console
aws lightsail reboot-instance --instance-name <name>

# Wait 60 seconds, then re-run deployment
```

---

## Monitoring Deployment Health

### Key Log Messages to Watch For:

✅ **Good signs:**
- `✅ dpkg is healthy`
- `✅ Pre-flight check passed`
- `✅ System health check passed`
- `✅ [dependency] installed successfully`

⚠️ **Warning signs (but deployment continues):**
- `⚠️ dpkg broken, fixing...`
- `⚠️ Retry attempt X/2`
- `⚠️ Health check had issues, but continuing...`

❌ **Error signs (deployment may fail):**
- `❌ dpkg is in broken state` (without fix message)
- `❌ All dependencies failed to install`
- `ssh: connect to host ... Operation timed out`

---

## Future Improvements

Consider adding:
1. **Automatic instance reboot** if health check fails critically
2. **Slack/email notifications** for deployment issues
3. **Metrics collection** for deployment success rates
4. **Automatic rollback** on deployment failure
5. **Blue-green deployments** for zero-downtime updates

---

## Related Documentation

- [DEPLOYMENT-TROUBLESHOOTING.md](./DEPLOYMENT-TROUBLESHOOTING.md) - Troubleshooting guide
- [UNIVERSAL-DEPLOYMENT.md](./UNIVERSAL-DEPLOYMENT.md) - Universal deployment guide
- [WORKFLOW_GUIDE.md](./WORKFLOW_GUIDE.md) - GitHub Actions workflow guide
