# Docker Deployment Debug & Fix Scripts

## debug-docker.py

**Purpose**: Comprehensive diagnostic tool for Docker deployments on AWS Lightsail Ubuntu instances.

### What It Does

This script connects to your Lightsail instance via SSH (using automatic key management) and performs 12 diagnostic checks:

#### 1. SSH Key Permissions
- Checks `.ssh` directory permissions
- Shows authorized_keys configuration
- Identifies SSH access issues

#### 2. Docker Service Status
- Checks if Docker daemon is running
- Shows service state, uptime, and process information
- Identifies if Docker failed to start

#### 3. Docker Version Check
- Verifies Docker is installed
- Shows Docker and Docker Compose versions
- Confirms Docker CLI is accessible

#### 4. Container Listing
- Lists all Docker containers (running and stopped)
- Shows container IDs, names, status, and ports
- Identifies containers that failed to start

#### 5. Container Logs
- Shows last 50 lines from all containers
- Identifies application errors and crashes
- Shows build and startup issues

#### 6. Docker Images
- Lists all Docker images on the system
- Shows image sizes and tags
- Identifies missing or corrupted images

#### 7. Docker Networks
- Lists Docker networks
- Shows network configuration
- Identifies network connectivity issues

#### 8. Disk Space Check
- Shows available disk space
- Identifies if disk is full
- Shows filesystem usage

#### 9. Docker System Info
- Shows Docker disk usage
- Lists images, containers, volumes, and cache
- Identifies space that can be reclaimed

#### 10. Container Connectivity Test
- Tests HTTP connectivity to each running container
- Verifies containers are responding
- Shows container health status

#### 11. Application Directory
- Lists files in `/opt/docker-app/`
- Shows deployed application structure
- Identifies missing files

#### 12. External Connectivity Test
- Performs curl request to localhost
- Shows HTTP response headers
- Verifies Docker containers are serving content

### Usage

```bash
# Source AWS credentials first
source .aws-creds.sh

# Run debug script
python3 troubleshooting-tools/docker/debug-docker.py

# When prompted:
Instance name [docker-lamp-demo]: docker-lamp-demo
AWS region [us-east-1]: us-east-1
```

### Example Output

```
🔍 Debugging Docker Deployment
================================================================================
📡 Sending command to ubuntu@54.159.160.207:

📋 1. Checking SSH key permissions:
drwx------ 2 ubuntu ubuntu 4096 Dec  4 18:30 .ssh
     ✅ SSH permissions correct

📋 2. Checking Docker service status:
● docker.service - Docker Application Container Engine
     Active: active (running) since Wed 2025-12-04 18:25:00 UTC
     ✅ Docker is running

📋 4. Listing all Docker containers:
CONTAINER ID   IMAGE                    STATUS
abc123def456   example-docker-app-web   Up 5 minutes
     ✅ Containers are running

📋 12. Testing external connectivity:
HTTP/1.1 200 OK
     ✅ Application is responding

✅ Debug complete
```

### Common Issues Detected

| Issue | Symptom in Output | Next Step |
|-------|------------------|-----------|
| Docker not running | `Active: inactive (dead)` | Run `fix-docker.py` |
| Container stopped | `Exited (1)` in container list | Check container logs |
| Build timeout | `Building` for 10+ minutes | Check Dockerfile optimization |
| Connection refused | `000` in connectivity test | Run `fix-docker.py` |
| Disk full | `100%` in disk space | Clean up images/containers |
| Port conflict | `port is already allocated` | Stop conflicting service |

---

## fix-docker.py

**Purpose**: Automated repair tool for common Docker deployment issues.

### What It Does

This script fixes the most common Docker deployment problems:

#### 1. Fix SSH Permissions
- Sets `.ssh` directory to `700`
- Sets `authorized_keys` to `600`
- Ensures SSH access works properly

#### 2. Enable Docker Service
- Enables Docker to start on boot
- Starts Docker service if stopped
- Ensures Docker daemon is running

#### 3. Add User to Docker Group
- Adds ubuntu user to docker group
- Allows running Docker without sudo
- Fixes permission denied errors

#### 4. Fix Docker Socket Permissions
- Sets `/var/run/docker.sock` to `666`
- Allows Docker commands to work
- Fixes socket permission errors

#### 5. Clean Stopped Containers
- Removes all stopped containers
- Frees up disk space
- Cleans up failed deployments

#### 6. Clean Unused Images
- Removes dangling images
- Frees up disk space
- Removes old build layers

#### 7. Restart Containers
- Stops all running containers
- Rebuilds images with latest code
- Starts containers with fresh state

#### 8. Wait for Initialization
- Waits 30 seconds for containers to start
- Allows services to fully initialize
- Ensures containers are ready

#### 9. Test Container Health
- Shows running containers
- Displays recent logs
- Verifies containers started successfully

#### 10. Test HTTP Access
- Performs local curl test
- Verifies application is serving content
- Confirms fix resolved issues

### Usage

```bash
# Source AWS credentials first
source .aws-creds.sh

# Run fix script interactively
python3 troubleshooting-tools/docker/fix-docker.py

# When prompted:
Instance name [docker-lamp-demo]: docker-lamp-demo
AWS region [us-east-1]: us-east-1
Reboot instance after fix? (y/N): n

# Or provide inputs automatically (no reboot)
echo -e "docker-lamp-demo\nus-east-1\nn" | python3 troubleshooting-tools/docker/fix-docker.py

# With reboot (recommended for stuck Docker daemon)
echo -e "docker-lamp-demo\nus-east-1\ny" | python3 troubleshooting-tools/docker/fix-docker.py
```

### Reboot Option

The fix script includes an optional reboot feature:

**When to reboot (answer 'y'):**
- Docker daemon won't start properly
- Containers are stuck or unresponsive
- After fixing multiple issues
- To test auto-start configuration
- Network issues persist after fixes

**When NOT to reboot (answer 'n'):**
- Simple permission fixes
- Production instances with active users
- Quick testing iterations
- Containers are already working

**What happens during reboot:**
- Graceful shutdown (~30 seconds)
- Instance restarts (~60 seconds)
- Docker auto-starts (~30 seconds)
- Containers auto-start (~60 seconds)
- Total downtime: ~2-3 minutes

### Example Output

```
🔧 Fixing Docker Deployment Issues
================================================================================

🔧 1. Fixing SSH key permissions...
✅ SSH permissions fixed

🔧 2. Checking Docker service...
✅ Docker service enabled and started

🔧 7. Restarting Docker containers...
Stopping containers...
Building images...
Starting containers...
✅ Containers restarted

🧪 Testing local access:
HTTP/1.1 200 OK
✅ Application is responding

✅ Docker deployment fixed successfully
```

### When to Use

Run this script when you encounter:
- ✅ Connection refused errors (HTTP 000)
- ✅ Docker daemon not running
- ✅ Permission denied errors
- ✅ Containers not starting
- ✅ After deployment timeouts
- ✅ Build failures
- ✅ Network connectivity issues

### What It Doesn't Fix

This script cannot fix:
- ❌ Dockerfile syntax errors
- ❌ Application code bugs
- ❌ Database connection issues (wrong credentials)
- ❌ Missing environment variables
- ❌ Port conflicts with other services
- ❌ Insufficient instance resources (RAM/CPU)

For these issues, check deployment logs or run `debug-docker.py` for more information.

---

## Workflow

```
Deployment Issue
       ↓
Run debug-docker.py
       ↓
Review diagnostic output
       ↓
Run fix-docker.py
       ↓
Re-run debug-docker.py to verify
       ↓
Issue resolved ✅
```

## Prerequisites

- AWS credentials configured (`.aws-creds.sh`)
- Python 3 with boto3 installed
- SSH access to Lightsail instance (automatic via `get_instance_access_details`)
- Instance running Ubuntu OS with Docker installed

## SSH Key Management

**Note**: These scripts use AWS Lightsail's `get_instance_access_details()` API which automatically provides temporary SSH keys and certificates. You don't need to manage SSH keys manually - the connection is handled automatically by the `LightsailBase` class.

If you see SSH connection errors, it's likely a network or firewall issue, not a key problem.
