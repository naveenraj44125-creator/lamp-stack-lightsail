# MCP Server Usage Examples

Real-world examples of using the Lightsail Deployment MCP Server with AI assistants.

## Example 1: Create a New Node.js API

**User:** "I want to create a new Node.js API called 'user-service' and deploy it to Lightsail in us-west-2"

**AI Response:**
```
I'll help you set up a new Node.js API with Lightsail deployment.

[Uses setup_new_repository tool with:
- repo_name: "user-service"
- app_type: "nodejs"
- instance_name: "user-service-prod"
- aws_region: "us-west-2"]

✅ Repository setup prepared!

Next Steps:
1. Create GitHub repository: gh repo create user-service --public
2. Copy files from: /tmp/lightsail-1733587200
3. Push to GitHub
4. Set up OIDC authentication

Configuration Generated:
- Instance: user-service-prod
- Region: us-west-2
- Type: nodejs
- Bucket: Disabled
- Database: none

Files Created:
- .github/workflows/deploy-generic-reusable.yml
- deployment-nodejs.config.yml
- workflows/*.py
```

## Example 2: Add Deployment to Existing React App

**User:** "Add Lightsail deployment to my existing React app at ./my-react-app with S3 bucket support"

**AI Response:**
```
I'll integrate Lightsail deployment into your React application.

[Uses integrate_existing_repository tool with:
- repo_path: "./my-react-app"
- app_type: "react"
- instance_name: "my-react-app"
- enable_bucket: true]

✅ Lightsail deployment integrated!

Added to ./my-react-app:
- .github/workflows/ (GitHub Actions)
- workflows/ (Python deployment scripts)
- deployment-react.config.yml

Next Steps:
1. Set up AWS OIDC authentication
2. Commit and push changes
3. Deployment will trigger automatically

Test locally:
cd ./my-react-app
git add .
git commit -m "Add Lightsail deployment"
git push origin main
```

## Example 3: Generate LAMP Stack Config with Database

**User:** "Generate a deployment config for a LAMP stack with PostgreSQL and Redis"

**AI Response:**
```
I'll generate a LAMP stack configuration with PostgreSQL and Redis.

[Uses generate_deployment_config tool with:
- app_type: "lamp"
- instance_name: "lamp-app"
- dependencies: ["redis"]
- database_type: "postgresql"]

# Deployment Configuration

```yaml
# LAMP Deployment Configuration
aws:
  region: us-east-1

lightsail:
  instance_name: lamp-app
  static_ip: ""

application:
  name: lamp-app
  version: "1.0.0"
  type: lamp
  package_fallback: true

dependencies:
  apache:
    enabled: true
  php:
    enabled: true
  mysql:
    enabled: true
  redis:
    enabled: true
  postgresql:
    enabled: true
    external: false

deployment:
  use_docker: false
  
monitoring:
  health_check:
    endpoint: "/"
    max_attempts: 10
```

Save this as `deployment-lamp.config.yml` in your repository root.
```

## Example 4: Set Up OIDC for Organization

**User:** "Set up OIDC authentication for my-org/api-gateway repository"

**AI Response:**
```
I'll provide the commands to set up GitHub Actions OIDC for AWS.

[Uses setup_oidc_authentication tool with:
- repo_owner: "my-org"
- repo_name: "api-gateway"
- role_name: "github-actions-lightsail"]

# Set up GitHub Actions OIDC for AWS

Run these AWS CLI commands:

```bash
# 1. Create OIDC provider (if doesn't exist)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# 2. Create IAM role
aws iam create-role \
  --role-name github-actions-lightsail \
  --assume-role-policy-document '{...}'

# 3-6. [Additional commands for policies]

# Get role ARN
aws iam get-role --role-name github-actions-lightsail --query 'Role.Arn' --output text
```

Then set GitHub variable:
```bash
gh variable set AWS_ROLE_ARN --body "arn:aws:iam::ACCOUNT_ID:role/github-actions-lightsail"
```
```

## Example 5: Check Deployment Status

**User:** "What's the status of my deployments?"

**AI Response:**
```
Let me check your deployment status.

[Uses get_deployment_status tool with:
- repo_path: "."]

# Deployment Status

✅ **Deploy to Lightsail** - completed
   https://github.com/my-org/api-gateway/actions/runs/7234567890
   Duration: 3m 42s
   Deployed: 2 hours ago

✅ **Deploy to Lightsail** - completed
   https://github.com/my-org/api-gateway/actions/runs/7234567889
   Duration: 3m 38s
   Deployed: 1 day ago

❌ **Deploy to Lightsail** - failure
   https://github.com/my-org/api-gateway/actions/runs/7234567888
   Duration: 1m 12s
   Failed: 2 days ago
   Error: Health check timeout

🔄 **Deploy to Lightsail** - in_progress
   https://github.com/my-org/api-gateway/actions/runs/7234567891
   Started: 30 seconds ago
```

## Example 6: List Available Templates

**User:** "What example applications can I deploy?"

**AI Response:**
```
Here are all available example applications:

[Uses list_available_examples tool]

# Available Example Applications

## 1. LAMP Stack
- Apache + PHP + MySQL/PostgreSQL
- Redis caching
- S3 bucket integration
- Perfect for: WordPress, Laravel, custom PHP apps

## 2. NGINX
- Static file serving
- Reverse proxy support
- SSL/TLS ready
- Perfect for: Static sites, SPAs, documentation

## 3. Node.js
- PM2 process manager
- NPM/Yarn support
- Database integration
- Perfect for: Express, Next.js, NestJS, APIs

## 4. Python
- Gunicorn WSGI server
- Virtual environment
- pip packages
- Perfect for: Flask, Django, FastAPI

## 5. React
- Production builds
- NGINX serving
- Environment variables
- Perfect for: CRA, Vite, Next.js static

## 6. Docker
- Multi-container architecture
- Docker Compose orchestration
- S3 bucket integration (optional)
- Perfect for: Complex apps, microservices

All examples include:
- Automatic deployment on push
- Health checks
- Monitoring
- S3 bucket support (optional)
- RDS database support (optional)
```

## Example 7: Complex Setup with All Features

**User:** "Create a new Docker app called 'recipe-app' with PostgreSQL RDS, S3 bucket, and deploy to us-east-1"

**AI Response:**
```
I'll set up a complete Docker application with all features.

[Uses setup_new_repository tool with:
- repo_name: "recipe-app"
- app_type: "docker"
- instance_name: "recipe-app-prod"
- aws_region: "us-east-1"
- enable_bucket: true
- bucket_name: "recipe-app-media"
- database_type: "postgresql"
- use_rds: true]

✅ Repository setup prepared!

Configuration Generated:
- Instance: recipe-app-prod
- Region: us-east-1
- Type: docker
- Bucket: Enabled (recipe-app-media)
- Database: postgresql (RDS)

This setup includes:
✅ Docker Compose orchestration
✅ PostgreSQL RDS database
✅ S3 bucket for media storage
✅ Automatic health checks
✅ GitHub Actions workflows
✅ OIDC authentication setup

Next Steps:
1. Create repository: gh repo create recipe-app --public
2. Copy files and push to GitHub
3. Run OIDC setup commands
4. Create RDS instance
5. Set database credentials in GitHub secrets
6. Push code to trigger deployment
```

## Example 8: Troubleshooting Deployment Issues

**User:** "My deployment isn't working, can you diagnose the problem?"

**AI Response:**
```
I'll run a complete diagnostic check on your deployment setup.

[Uses diagnose_deployment tool with:
- repo_path: "."
- check_type: "all"]

# Deployment Diagnostics Report

## Prerequisites Check

✅ Node.js: v20.19.0
✅ GitHub CLI: gh version 2.40.0
✅ AWS CLI: aws-cli/2.13.0
✅ Git: git version 2.42.0

## GitHub Configuration

✅ GitHub CLI: Authenticated
✅ Git repository: Found
   Remote: https://github.com/user/my-app.git

## AWS Configuration

⚠️  AWS Credentials: Not configured
   Run: aws configure

⚠️  GitHub OIDC Provider: Not found
   Use setup_oidc_authentication tool to configure

## Deployment Configuration

✅ Deployment Config: Found 1 file(s)
   - deployment-nodejs.config.yml
✅ GitHub Actions: Workflows found
✅ Deployment Scripts: Found

## Lightsail Instance

   Instance Name: my-app-prod
⚠️  Instance: Not found or not accessible

## Summary

✅ Passed: 8
⚠️  Warnings: 3
❌ Issues: 0

### Warnings
- AWS credentials not configured
- GitHub OIDC provider not found
- Instance my-app-prod not found or not accessible

## Recommendations

Please address the issues and warnings above before deploying.

**Quick Fixes:**
- Configure AWS: `aws configure`
- Set up OIDC: Use setup_oidc_authentication tool

---

For detailed troubleshooting, see: TROUBLESHOOTING.md
```

**Follow-up User:** "How do I configure AWS credentials?"

**AI Response:**
```
Run this command and provide your AWS credentials:

```bash
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

After configuring, I can help you set up OIDC authentication.
```

## Tips for Using the MCP Server

1. **Be Specific**: Include instance names, regions, and features you need
2. **Ask for Help**: Use "list available examples" to see what's possible
3. **Check Status**: Regularly monitor deployments with "get deployment status"
4. **Iterate**: Start simple, then add features like buckets and databases
5. **Follow Steps**: The AI will guide you through the setup process

## Common Workflows

### New Project
1. List examples → Choose app type → Setup new repository → Configure OIDC → Deploy

### Existing Project
1. Integrate existing repository → Configure OIDC → Commit and push → Monitor deployment

### Configuration Only
1. Generate deployment config → Customize → Add to repository → Deploy

### Troubleshooting
1. Check deployment status → Review logs → Adjust configuration → Redeploy
