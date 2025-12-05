# Docker Deployment Issues & Analysis

## Current Status: FIXED ✅ (December 5, 2025)

### Latest Fix: Network Timeout & Missing Import
**Issue**: Docker Hub timeout errors (`server 100.31.83.7 not responding`) when pulling pre-built images

**Root Cause**:
1. Missing `import os` statement causing `os.environ.get()` to fail
2. Short timeout (300s) for Docker image pulls
3. No retry logic for network failures
4. No network diagnostics

**Solution Applied**:
- ✅ Added missing `import os` statement
- ✅ Increased pull timeout from 300s to 600s (10 minutes)
- ✅ Implemented 3-attempt retry logic with delays
- ✅ Added network connectivity checks (ping, DNS)
- ✅ Configured Docker daemon with optimized settings
- ✅ Added Docker Hub connectivity diagnostics

**Files Changed**: `workflows/deploy-post-steps-generic.py`

---

## Previous Issues (Resolved)

Docker deployments were failing due to build timeouts and container startup issues.

## Root Cause Analysis

### Primary Issue: Docker Build Timeouts
The Docker image build process is taking 10-15+ minutes on Lightsail nano instances, causing:
1. **Post-deployment timeout** (30 minutes) - Build exceeds this limit
2. **SSH connection instability** - Long-running builds cause SSH to timeout
3. **Instance resource exhaustion** - Nano instances (512MB RAM) struggle with Docker builds

### Secondary Issues
1. **Empty IP Address in Verification** - URL shows `http:///` instead of actual IP
2. **No Containers Running** - `/opt/docker-app/` directory is empty after "successful" deployment
3. **Instance Instability** - SSH connections timeout, instances become unresponsive

## What We've Tried

### ✅ Dockerfile Optimization (85-90% improvement)
- **Before**: Ubuntu 22.04 base + full LAMP stack installation (70+ lines, 10-15 min build)
- **After**: Official `php:8.1-apache` base image (25-30 lines, should be 1-3 min)
- **Result**: Still timing out - build happens on slow Lightsail instance

### ✅ Timeout Increases
- Post-steps timeout: 15min → 30min
- Build timeout: 600s → 900s  
- Container startup wait: 180s → 300s
- Verification wait: 30s → 60s, attempts 10 → 15
- **Result**: Not enough - builds still exceed limits

### ✅ Fresh Instance
- Created new instance `docker-lamp-demo-v2` (100.31.83.7)
- Old instance had SSH issues and was stuck
- **Result**: Same timeout issues on fresh instance

## Current Deployment Flow Issues

```
GitHub Actions
    ↓
Upload code to Lightsail
    ↓
SSH to instance
    ↓
Run docker-compose build  ← FAILS HERE (10-15+ minutes)
    ↓
Timeout / SSH disconnect
    ↓
Verification fails (no containers running)
```

## Solutions to Consider

### Option 1: Build on GitHub Actions (RECOMMENDED)
**Pros:**
- Fast GitHub runners (8GB RAM, multi-core)
- Build once, deploy anywhere
- Can cache layers between builds
- No Lightsail resource constraints

**Cons:**
- Need container registry (ECR, Docker Hub)
- More complex workflow
- Additional AWS permissions needed

**Implementation:**
```yaml
- name: Build Docker image
  run: docker build -t my-app:${{ github.sha }} .
  
- name: Push to ECR
  run: |
    aws ecr get-login-password | docker login --username AWS --password-stdin
    docker push my-app:${{ github.sha }}
    
- name: Deploy to Lightsail
  run: |
    ssh instance "docker pull my-app:${{ github.sha }}"
    ssh instance "docker-compose up -d"
```

### Option 2: Use Larger Instance Size
**Pros:**
- Simple - just change bundle size
- More resources for builds

**Cons:**
- Higher cost ($7/month for small vs $3.50 for nano)
- Still slower than GitHub runners
- Doesn't solve fundamental architecture issue

**Implementation:**
```yaml
lightsail:
  instance_name: docker-lamp-demo-v2
  bundle_id: small_3_0  # 2GB RAM instead of 512MB
```

### Option 3: Pre-built Base Images
**Pros:**
- Minimal build time on instance
- Can version control images

**Cons:**
- Need to maintain base images
- Still requires registry

### Option 4: Traditional LAMP Deployment
**Pros:**
- Works reliably (lamp-stack-demo-v2 is working)
- No Docker overhead
- Faster deployments

**Cons:**
- Less portable
- Manual dependency management
- Not using Docker benefits

## Recommended Path Forward

### Short Term: Use Traditional LAMP
The regular LAMP deployment works fine. Docker adds complexity without clear benefits for simple PHP apps.

### Long Term: Proper Docker CI/CD
If Docker is required:
1. Set up AWS ECR repository
2. Build images in GitHub Actions
3. Push to ECR
4. Pull and run on Lightsail
5. Use at least `small_3_0` bundle (2GB RAM)

## Test Results

### Instance: docker-lamp-demo-v2
- **IP**: 100.31.83.7
- **Status**: Running
- **Docker**: Installed and running
- **Containers**: None (deployment failed)
- **Application**: Not deployed (/opt/docker-app/ empty)

### Diagnostic Output
```bash
📋 4. Listing all Docker containers:
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
# Empty - no containers

📋 5. Checking Docker container logs:
No docker-compose found

📋 11. Checking application directory:
ls: cannot access '/opt/docker-app/': No such file or directory

📋 12. Testing external connectivity:
curl: (7) Failed to connect to localhost port 80
```

## Files Created for Troubleshooting

- `troubleshooting-tools/docker/debug-docker.py` - Diagnostic script
- `troubleshooting-tools/docker/fix-docker.py` - Automated fixes
- `troubleshooting-tools/docker/README.md` - Documentation
- `DOCKER-BUILD-OPTIMIZATION.md` - Dockerfile optimization guide
- `monitor-docker-deployments.sh` - Monitoring script

## Next Steps

1. **Decision needed**: Continue with Docker or switch to traditional LAMP?
2. If Docker: Implement GitHub Actions build + ECR push
3. If LAMP: Use existing working deployment system
4. Consider instance size upgrade if staying with Docker

## Related Documentation

- [DOCKER-BUILD-OPTIMIZATION.md](DOCKER-BUILD-OPTIMIZATION.md) - Dockerfile improvements
- [DOCKER-DEPLOYMENT-FIXES.md](DOCKER-DEPLOYMENT-FIXES.md) - Previous fix attempts
- [troubleshooting-tools/docker/README.md](troubleshooting-tools/docker/README.md) - Debug tools
