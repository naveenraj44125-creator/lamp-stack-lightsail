# Docker Hub Setup for Pre-Built Images

## Overview

This guide explains how to set up Docker Hub integration so GitHub Actions can build images once and deploy them quickly to Lightsail.

## Benefits

- **Fast builds**: Build on GitHub runners (8GB RAM) instead of Lightsail nano (512MB RAM)
- **Build time**: ~2-3 minutes on GitHub vs 10-15+ minutes on Lightsail
- **Reliable deployments**: No more timeout issues
- **Caching**: GitHub Actions caches layers between builds
- **Deploy anywhere**: Same image can be deployed to multiple instances

## Prerequisites

1. Docker Hub account (free tier works fine)
2. GitHub repository with Actions enabled
3. AWS Lightsail instance with Docker installed

## Step 1: Create Docker Hub Account

1. Go to https://hub.docker.com/
2. Sign up for free account
3. Verify your email

## Step 2: Create Docker Hub Access Token

1. Log in to Docker Hub
2. Go to Account Settings → Security
3. Click "New Access Token"
4. Name: `github-actions-lamp-stack`
5. Permissions: Read, Write, Delete
6. Click "Generate"
7. **Copy the token** (you won't see it again!)

## Step 3: Add GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"

Add these two secrets:

### DOCKER_USERNAME
- Name: `DOCKER_USERNAME`
- Value: Your Docker Hub username (e.g., `johndoe`)

### DOCKER_PASSWORD
- Name: `DOCKER_PASSWORD`
- Value: The access token you generated in Step 2

## Step 4: Update docker-compose.yml (Already Done)

The `docker-compose.yml` now supports both modes:

```yaml
services:
  web:
    # Uses DOCKER_IMAGE env var if set, otherwise builds locally
    image: ${DOCKER_IMAGE:-lamp-stack-demo-web:local}
    build:
      context: .
      dockerfile: Dockerfile
```

## Step 5: Deploy

The workflow is already configured! Just push your changes:

```bash
git add .
git commit -m "Enable Docker Hub pre-built images"
git push
```

## How It Works

### Build Phase (GitHub Actions)
```
1. Checkout code
2. Set up Docker Buildx
3. Log in to Docker Hub
4. Build image (2-3 minutes on fast GitHub runner)
5. Push to Docker Hub
6. Tag: yourusername/lamp-stack-demo:main-abc1234
```

### Deploy Phase (Lightsail)
```
1. SSH to Lightsail instance
2. Pull pre-built image from Docker Hub (30 seconds)
3. Pull service images (MySQL, Redis, etc.)
4. Start containers with docker-compose up
5. Verify deployment
```

## Image Naming Convention

Images are tagged with:
- `yourusername/lamp-stack-demo:main-abc1234` (branch + commit SHA)
- `yourusername/lamp-stack-demo:main` (latest on branch)
- `yourusername/lamp-stack-demo:latest` (latest on default branch)

## Testing Locally

You can pull and test the same image locally:

```bash
# Pull the image
docker pull yourusername/lamp-stack-demo:main

# Run it
export DOCKER_IMAGE=yourusername/lamp-stack-demo:main
docker-compose up -d
```

## Troubleshooting

### "unauthorized: incorrect username or password"
- Check DOCKER_USERNAME and DOCKER_PASSWORD secrets
- Regenerate Docker Hub access token
- Ensure token has Read, Write permissions

### "repository does not exist"
- First push creates the repository automatically
- Make sure Docker Hub username is correct
- Check image name matches your username

### "rate limit exceeded"
- Docker Hub free tier: 100 pulls per 6 hours
- Upgrade to Pro ($5/month) for unlimited pulls
- Or use AWS ECR instead

## Alternative: AWS ECR

If you prefer AWS ECR instead of Docker Hub:

1. Create ECR repository
2. Update workflow to use `aws-actions/amazon-ecr-login@v2`
3. Change image name to ECR format
4. Add ECR permissions to GitHub OIDC role

## Cost Comparison

### Docker Hub (Current Setup)
- Free tier: Unlimited private repos, 100 pulls/6hrs
- Pro: $5/month for unlimited

### AWS ECR
- $0.10 per GB-month storage
- $0.09 per GB data transfer
- ~$1-2/month for small apps

## Monitoring

Check Docker Hub for:
- Image sizes
- Pull counts
- Storage usage

## Security Notes

- Access tokens are safer than passwords
- Tokens can be revoked anytime
- Use separate tokens for different projects
- Never commit tokens to code

## Next Steps

1. Create Docker Hub account
2. Generate access token
3. Add GitHub secrets
4. Push code to trigger build
5. Watch deployment succeed in ~5 minutes instead of 20+!
