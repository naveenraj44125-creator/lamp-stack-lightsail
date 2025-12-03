# Lightsail GitHub Actions Integration Guide

## Overview

This guide helps you add automated AWS Lightsail deployment to your existing GitHub repository.

## Quick Start

### For Existing Repositories

Run the integration script in your repository:

```bash
cd /path/to/your/repo
curl -sL https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/integrate-lightsail-actions.sh | bash
```

Or download and run locally:

```bash
wget https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/integrate-lightsail-actions.sh
chmod +x integrate-lightsail-actions.sh
./integrate-lightsail-actions.sh
```

### For New Repositories

Use the setup script to create a new repository:

```bash
./setup-new-repo.sh
```

## What Gets Installed

The integration script adds:

### 1. GitHub Actions Workflows
- `.github/workflows/deploy-to-lightsail.yml` - Main deployment workflow
- `.github/workflows/deploy-generic-reusable.yml` - Reusable workflow engine

### 2. Deployment Configuration
- `deployment-{type}.config.yml` - Your application's deployment config
- Customizable dependencies, environment variables, and settings

### 3. Automation Scripts
- `workflows/lightsail_common.py` - Core Lightsail operations
- `workflows/lightsail_rds.py` - RDS database management
- `workflows/lightsail_bucket.py` - S3 bucket integration
- `workflows/dependency_manager.py` - Dependency installation
- `workflows/deployment_monitor.py` - Health checks and monitoring
- Additional helper modules

### 4. Documentation
- `LIGHTSAIL-DEPLOYMENT.md` - Setup and usage guide

## Supported Application Types

### 1. LAMP Stack (Apache + PHP + MySQL/PostgreSQL)
- Apache web server
- PHP 8.3 with extensions
- MySQL or PostgreSQL (local or RDS)
- Composer support
- Redis caching

**Best for:** WordPress, Laravel, custom PHP apps

### 2. NGINX (Static Sites)
- NGINX web server
- Static file serving
- Reverse proxy support
- SSL/TLS configuration

**Best for:** Static websites, SPAs, documentation sites

### 3. Node.js
- Node.js 18+
- NPM/Yarn support
- PM2 process manager
- Database support (MySQL/PostgreSQL)

**Best for:** Express, Next.js, NestJS, API servers

### 4. Python
- Python 3.9+
- Virtual environment
- pip package management
- WSGI server (Gunicorn)
- Database support

**Best for:** Flask, Django, FastAPI, data apps

### 5. React
- Build optimization
- NGINX serving
- Environment variable injection
- Production builds

**Best for:** Create React App, Vite, Next.js static exports

## Features

### Automatic Deployment
- ✅ Triggers on push to main/master
- ✅ Manual workflow dispatch
- ✅ Pull request testing (optional)

### Infrastructure Management
- ✅ Auto-creates Lightsail instance if needed
- ✅ Configures firewall rules
- ✅ Assigns static IP
- ✅ Sets up SSH access

### Database Support
- ✅ Local MySQL/PostgreSQL installation
- ✅ External RDS integration
- ✅ Automatic connection configuration
- ✅ Database credentials management

### S3 Bucket Integration
- ✅ Automatic bucket creation
- ✅ Instance attachment with credentials
- ✅ Read-only or read-write access
- ✅ Multiple size options (250GB - 1TB)

### Dependency Management
- ✅ Automatic dependency installation
- ✅ Version control
- ✅ Service configuration
- ✅ Performance optimization

### Monitoring & Health Checks
- ✅ Deployment verification
- ✅ HTTP endpoint testing
- ✅ Service status checks
- ✅ Detailed logging

## Configuration Options

### Basic Configuration

```yaml
lightsail:
  instance_name: "my-app-prod"
  blueprint_id: "ubuntu_22_04"
  bundle_id: "nano_3_0"  # 512MB RAM, 1 vCPU
```

### Database Configuration

```yaml
dependencies:
  mysql:
    enabled: true
    external: true  # Use RDS
    rds:
      database_name: "my-rds-instance"
      region: "us-east-1"
      master_database: "app_db"
```

### Bucket Configuration

```yaml
lightsail:
  bucket:
    enabled: true
    name: "my-app-bucket"
    access_level: "read_write"
    bundle_id: "small_1_0"  # 250GB
```

### Application Files

```yaml
application:
  package_files:
    - "*.php"
    - "src/"
    - "public/"
    - "config/"
```

## AWS Authentication Setup

### Option 1: OIDC (Recommended)

Run the OIDC setup script:

```bash
./setup-github-oidc.sh
```

This creates an IAM role with proper permissions and trust policy.

### Option 2: Existing Role

If you already have an IAM role:

1. Go to GitHub repository Settings
2. Navigate to Secrets and variables → Actions
3. Add variable: `AWS_ROLE_ARN`
4. Value: Your role ARN (e.g., `arn:aws:iam::123456789:role/GitHubActionsRole`)

## Deployment Process

### 1. Initial Setup

```bash
# Run integration script
./integrate-lightsail-actions.sh

# Configure AWS authentication
./setup-github-oidc.sh  # or add AWS_ROLE_ARN variable

# Commit changes
git add .
git commit -m "Add Lightsail deployment"
git push origin main
```

### 2. Automatic Deployment

Every push to main triggers:
1. Code checkout
2. Dependency installation
3. Application packaging
4. Instance provisioning (if needed)
5. File deployment
6. Service configuration
7. Health checks

### 3. Manual Deployment

Trigger from GitHub UI:
1. Go to Actions tab
2. Select "Deploy to AWS Lightsail"
3. Click "Run workflow"
4. Choose branch and run

## Customization

### Add Custom Dependencies

Edit `deployment-{type}.config.yml`:

```yaml
dependencies:
  redis:
    enabled: true
    version: "latest"
  
  docker:
    enabled: true
    config:
      enable_compose: true
```

### Custom Environment Variables

```yaml
application:
  environment_variables:
    APP_ENV: production
    API_KEY: "your-key"
    CUSTOM_VAR: "value"
```

### Custom Deployment Steps

```yaml
deployment:
  steps:
    post_deployment:
      common:
        enabled: true
        verify_extraction: true
        create_env_file: true
```

## Troubleshooting

### Deployment Fails

1. **Check GitHub Actions logs**
   - Go to Actions tab
   - Click on failed workflow
   - Review step-by-step logs

2. **Verify AWS credentials**
   - Ensure AWS_ROLE_ARN is set
   - Check IAM role permissions
   - Verify trust policy

3. **Check instance status**
   - Log into AWS Lightsail console
   - Verify instance is running
   - Check firewall rules

### Connection Issues

```bash
# SSH into instance
ssh ubuntu@<instance-ip>

# Check service status
sudo systemctl status apache2  # or nginx, pm2, etc.

# View logs
sudo tail -f /var/log/apache2/error.log
```

### Database Connection Fails

1. Verify RDS instance is running
2. Check security group rules
3. Verify database credentials in GitHub secrets
4. Test connection from instance

## Examples

### LAMP Stack with RDS

```yaml
dependencies:
  apache:
    enabled: true
  php:
    enabled: true
    version: "8.3"
  postgresql:
    enabled: true
    external: true
    rds:
      database_name: "my-postgres-db"
```

### Node.js API with Bucket

```yaml
dependencies:
  nodejs:
    enabled: true
    version: "18"
    config:
      npm_packages: ["pm2"]

lightsail:
  bucket:
    enabled: true
    name: "api-uploads"
    access_level: "read_write"
```

### React SPA with NGINX

```yaml
dependencies:
  nginx:
    enabled: true
    config:
      document_root: "/var/www/html"
  nodejs:
    enabled: true  # For build process
```

## Best Practices

1. **Use environment-specific configs**
   - Create separate configs for staging/production
   - Use different instance names

2. **Secure sensitive data**
   - Store credentials in GitHub Secrets
   - Never commit passwords or keys

3. **Test before deploying**
   - Enable PR testing
   - Use staging environment

4. **Monitor deployments**
   - Check GitHub Actions logs
   - Set up health check endpoints
   - Monitor instance metrics

5. **Regular backups**
   - Enable database backups
   - Use S3 buckets for file storage
   - Document recovery procedures

## Support

- **Documentation**: See LIGHTSAIL-DEPLOYMENT.md in your repo
- **Issues**: https://github.com/naveenraj44125-creator/lamp-stack-lightsail/issues
- **Examples**: Check example-*-app directories

## License

MIT License - Feel free to use and modify for your projects.
