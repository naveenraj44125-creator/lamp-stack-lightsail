# 🚀 Deployment Guide - Basic Docker LAMP

## GitHub Actions Workflow

This example has its own dedicated GitHub Actions workflow: `.github/workflows/deploy-docker-basic.yml`

## 🎯 Automatic Deployment

The workflow automatically triggers on:

### 1. Push to Main/Master
```bash
git add .
git commit -m "Update Docker app"
git push origin main
```

**Triggers when**:
- Any file in `example-docker-app/` changes
- `deployment-docker.config.yml` changes
- The workflow file itself changes

### 2. Pull Request
```bash
git checkout -b feature/my-changes
# Make changes
git push origin feature/my-changes
# Create PR on GitHub
```

**Note**: PR deployments are disabled by default. Enable in config:
```yaml
github_actions:
  jobs:
    deployment:
      deploy_on_pr: true  # Change to true
```

### 3. Manual Trigger

**Via GitHub UI**:
1. Go to **Actions** tab
2. Select **Deploy Basic Docker LAMP**
3. Click **Run workflow**
4. Choose branch and environment
5. Click **Run workflow**

**Via GitHub CLI**:
```bash
gh workflow run deploy-docker-basic.yml
```

## 📋 Deployment Configuration

Edit `deployment-docker.config.yml`:

```yaml
lightsail:
  instance_name: docker-lamp-demo-v1  # Change this

dependencies:
  docker:
    enabled: true
    config:
      install_compose: true

deployment:
  use_docker: true  # Must be true for Docker deployment
```

## 🔍 Monitor Deployment

### View Logs
1. Go to **Actions** tab on GitHub
2. Click on the running workflow
3. Click on **Deploy Basic Docker LAMP to Lightsail**
4. View real-time logs

### Check Status
```bash
# After deployment, SSH to instance
ssh ubuntu@your-instance-ip

# Check containers
sudo docker-compose ps

# View logs
sudo docker-compose logs -f
```

## ⏱️ Deployment Timeline

| Step | Duration | Description |
|------|----------|-------------|
| **Checkout Code** | 10s | Clone repository |
| **Setup Python** | 20s | Install dependencies |
| **Install Docker** | 5-8 min | First time only |
| **Download Images** | 5-10 min | MySQL, Redis, etc. |
| **Build Custom Image** | 3-5 min | Apache + PHP |
| **Start Containers** | 1-2 min | Launch services |
| **Health Checks** | 1-2 min | Verify deployment |

**Total**: 15-25 minutes (first deployment), 2-5 minutes (subsequent)

## 🎛️ Workflow Inputs

When manually triggering, you can specify:

- **environment**: `production` (default), `staging`, `development`

## 🔧 Troubleshooting

### Workflow Not Triggering

**Check**:
1. File paths match trigger patterns
2. Branch is `main` or `master`
3. Workflow file is in `.github/workflows/`

**Fix**:
```bash
# Trigger manually
gh workflow run deploy-docker-basic.yml
```

### Deployment Fails

**Check logs**:
1. GitHub Actions tab
2. Failed workflow run
3. Expand failed step

**Common issues**:
- Docker installation timeout → Increase timeout in config
- Image download fails → Check network/retry
- Container won't start → Check docker-compose.yml syntax

### Access Denied

**Check**:
1. GitHub secrets configured (AWS credentials)
2. IAM role has correct permissions
3. OIDC provider set up correctly

**Fix**: Run `./setup-github-oidc.sh`

## 📊 Deployment Status

After successful deployment:

```
✅ Instance: http://your-instance-ip/
✅ Dashboard: http://your-instance-ip/
✅ API Test: http://your-instance-ip/api/test.php
✅ phpMyAdmin: http://your-instance-ip:8080
```

## 🔄 Rollback

If deployment fails or has issues:

```bash
# SSH to instance
ssh ubuntu@your-instance-ip

# Stop containers
cd /opt/docker-app
sudo docker-compose down

# Restore from backup
sudo cp -r /var/backups/docker-deployments/latest/* .

# Start containers
sudo docker-compose up -d
```

## 📚 Related Documentation

- [Docker Deployment Guide](../../DOCKER-DEPLOYMENT-GUIDE.md)
- [Docker Examples Comparison](../../DOCKER-EXAMPLES-GUIDE.md)
- [Main README](../../README.md)

---

**Need help?** Check the [troubleshooting section](../../DOCKER-DEPLOYMENT-GUIDE.md#troubleshooting) or open an issue.
