# GitHub Integration Guide - Direct Deployment Setup

Deploy your applications to AWS Lightsail using GitHub Actions without any MCP server dependencies. This guide provides complete automation for LAMP, Node.js, Python, React, Docker, and NGINX applications.

## 🚀 Quick Start

### Option 1: Create Repository First (Recommended)

To avoid username detection issues, create your GitHub repository first:

```bash
# Create GitHub repository with proper naming
gh repo create reddit-app --private --description "reddit-app Node.js, MySQL, and AWS Lightsail deployment"

# Clone the repository
git clone https://github.com/YOUR_USERNAME/reddit-app.git
cd reddit-app

# Download the setup script
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh
chmod +x setup-complete-deployment.sh

# Configure environment variables
export AUTO_MODE=true
export AWS_REGION="us-east-1"
export APP_TYPE="nodejs"
export APP_NAME="Reddit App"
export INSTANCE_NAME="reddit-app-instance"
export DATABASE_TYPE="mysql"
export DB_EXTERNAL="true"
export DB_RDS_NAME="reddit-app-mysql-db"
export DB_NAME="reddit_db"
export ENABLE_BUCKET="true"
export BUCKET_NAME="reddit-app-storage"
export GITHUB_REPO="YOUR_USERNAME/reddit-app"  # Include your username!

# Run the setup
./setup-complete-deployment.sh --auto
```

### Option 2: One-Command Setup (Advanced Users)

Download and run the complete deployment setup script:

```bash
# Download the script
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh

# Make it executable  
chmod +x setup-complete-deployment.sh

# Set environment variables for fully automated deployment
export AUTO_MODE=true
export AWS_REGION="us-east-1"
export APP_VERSION="1.0.0"
export APP_TYPE="nodejs"
export APP_NAME="social-media-app-deployment"
export INSTANCE_NAME="social-media-app-deployment-instance"
export BLUEPRINT_ID="ubuntu_22_04"
export BUNDLE_ID="small_3_0"
export DATABASE_TYPE="postgresql"
export DB_EXTERNAL="true"
export DB_RDS_NAME="social-media-app-deployment-rds"
export DB_NAME="nodejs_app_db"
export ENABLE_BUCKET="true"
export BUCKET_NAME="social-media-app-deployment-bucket"
export BUCKET_ACCESS="read_write"
export BUCKET_BUNDLE="small_1_0"
export GITHUB_REPO="social-media-app-deployment"
export REPO_VISIBILITY="public"

# Run the script in fully automated mode
./setup-complete-deployment.sh --auto --aws-region us-east-1 --app-version 1.0.0
```

### Option 2: Interactive Setup

For step-by-step configuration with prompts:

```bash
# Download and run interactively
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh
chmod +x setup-complete-deployment.sh
./setup-complete-deployment.sh
```

## 📋 Prerequisites

Before running the setup script, ensure you have:

### GitHub Repository Setup

**Best Practice**: Create your GitHub repository first to avoid username detection issues:

```bash
# Basic repository creation
gh repo create my-app --private --description "My application deployment"

# With specific application types
gh repo create lamp-blog --public --description "LAMP stack blog with MySQL and S3"
gh repo create nodejs-api --private --description "Node.js REST API with PostgreSQL"
gh repo create react-dashboard --public --description "React dashboard with NGINX"
gh repo create docker-microservices --private --description "Docker microservices with Redis"

# Clone and navigate to repository
git clone https://github.com/YOUR_USERNAME/my-app.git
cd my-app
```

**Repository Naming Conventions**:
- Use lowercase with hyphens: `my-awesome-app`
- Include technology stack: `nodejs-express-api`, `react-admin-panel`
- Be descriptive: `e-commerce-backend`, `portfolio-website`

**Common Repository Creation Examples**:
```bash
# Social media applications
gh repo create reddit-app --private --description "reddit-app Node.js, MySQL, and AWS Lightsail deployment"
gh repo create twitter-clone --public --description "Twitter clone with React and PostgreSQL"
gh repo create instagram-clone --private --description "Instagram clone with LAMP stack and S3 storage"

# Business applications
gh repo create e-commerce-api --private --description "E-commerce REST API with Node.js and PostgreSQL"
gh repo create inventory-system --private --description "Inventory management system with LAMP stack"
gh repo create crm-dashboard --public --description "CRM dashboard with React and MySQL"

# Portfolio and blogs
gh repo create portfolio-website --public --description "Personal portfolio with React and NGINX"
gh repo create tech-blog --public --description "Tech blog with LAMP stack and MySQL"
gh repo create company-website --private --description "Company website with Docker and PostgreSQL"
```

## 📋 System Prerequisites

Before running the setup script, ensure you have:

### Required Tools
- **Git** - Version control system
- **GitHub CLI (gh)** - GitHub command line tool
- **AWS CLI** - Amazon Web Services command line interface

### Installation Commands

**macOS (using Homebrew):**
```bash
# Install required tools
brew install git gh awscli

# Authenticate with GitHub
gh auth login

# Configure AWS credentials
aws configure
```

**Ubuntu/Debian:**
```bash
# Install Git and AWS CLI
sudo apt update
sudo apt install -y git awscli

# Install GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install -y gh

# Authenticate with GitHub
gh auth login

# Configure AWS credentials
aws configure
```

**Windows (using Chocolatey):**
```powershell
# Install required tools
choco install git github-cli awscli

# Authenticate with GitHub
gh auth login

# Configure AWS credentials
aws configure
```

### Authentication Setup

1. **GitHub Authentication:**
   ```bash
   gh auth login
   # Follow prompts to authenticate with your GitHub account
   ```

2. **AWS Configuration:**
   ```bash
   aws configure
   # Enter your AWS Access Key ID
   # Enter your AWS Secret Access Key
   # Enter your default region (e.g., us-east-1)
   # Enter output format (json)
   ```

## 🎯 Supported Application Types

The setup script supports six different application types:

### 1. LAMP Stack (Linux, Apache, MySQL, PHP)
```bash
export APP_TYPE="lamp"
export DATABASE_TYPE="mysql"  # or "postgresql"
```

### 2. Node.js Applications
```bash
export APP_TYPE="nodejs"
export DATABASE_TYPE="postgresql"  # or "mysql" or "none"
```

#### Fullstack React + Node.js Requirements

If your Node.js app has a React frontend in `/client`, you need these for deployment to work:

**1. Root package.json scripts:**
```json
{
  "scripts": {
    "build": "cd client && npm install && npm run build",
    "start": "cd server && npm start"
  }
}
```

**2. Server must serve React build in production (server/index.js):**
```javascript
const path = require('path');

// BEFORE your routes - serve static files
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../client/build')));
}

// Your API routes here...
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);

// AFTER your routes - SPA catch-all
if (process.env.NODE_ENV === 'production') {
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../client/build/index.html'));
  });
}
```

**3. Health check endpoint (required for deployment verification):**
```javascript
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'API is running' });
});
```

The setup script will warn you if these are missing, but won't auto-fix server code.

### 3. Python Applications (Flask/Django)
```bash
export APP_TYPE="python"
export DATABASE_TYPE="postgresql"  # or "mysql" or "none"
```

### 4. React Applications
```bash
export APP_TYPE="react"
export DATABASE_TYPE="none"  # Static sites typically don't need databases
```

### 5. Docker Applications
```bash
export APP_TYPE="docker"
export BUNDLE_ID="medium_3_0"  # Docker requires minimum 4GB RAM
```

### 6. NGINX Static Sites
```bash
export APP_TYPE="nginx"
export DATABASE_TYPE="none"
```

## ⚙️ Configuration Options

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AUTO_MODE` | No | `false` | Set to `true` for non-interactive mode |
| `AWS_REGION` | No | `us-east-1` | AWS region for deployment |
| `APP_VERSION` | No | `1.0.0` | Application version |
| `APP_TYPE` | Yes* | - | Application type (lamp, nodejs, python, react, docker, nginx) |
| `APP_NAME` | Yes* | - | Human-readable application name |
| `INSTANCE_NAME` | Yes* | - | Lightsail instance name |
| `BLUEPRINT_ID` | No | `ubuntu_22_04` | Operating system (ubuntu_22_04, ubuntu_20_04, amazon_linux_2023) |
| `BUNDLE_ID` | No | `small_3_0` | Instance size (nano_3_0, micro_3_0, small_3_0, medium_3_0, large_3_0) |
| `DATABASE_TYPE` | No | `none` | Database type (mysql, postgresql, none) |
| `DB_EXTERNAL` | No | `false` | Use external RDS database |
| `DB_RDS_NAME` | No | - | RDS instance name (if DB_EXTERNAL=true) |
| `DB_NAME` | No | `app_db` | Database name |
| `ENABLE_BUCKET` | No | `false` | Enable S3 bucket integration |
| `BUCKET_NAME` | No | - | S3 bucket name (if ENABLE_BUCKET=true) |
| `BUCKET_ACCESS` | No | `read_write` | Bucket access level (read_only, read_write) |
| `BUCKET_BUNDLE` | No | `small_1_0` | Bucket size (small_1_0, medium_1_0, large_1_0) |
| `GITHUB_REPO` | No | - | GitHub repository name |
| `REPO_VISIBILITY` | No | `private` | Repository visibility (public, private) |

*Required when `AUTO_MODE=true`
### Instance Size Guide

| Bundle ID | RAM | vCPU | Storage | Price/Month | Best For |
|-----------|-----|------|---------|-------------|----------|
| `nano_3_0` | 512MB | 1 | 20GB SSD | $3.50 | Minimal testing |
| `micro_3_0` | 1GB | 2 | 40GB SSD | $7.00 | Light workloads |
| `small_3_0` | 2GB | 2 | 60GB SSD | $12.00 | **Default for most apps** |
| `medium_3_0` | 4GB | 2 | 80GB SSD | $24.00 | **Required for Docker** |
| `large_3_0` | 8GB | 2 | 160GB SSD | $44.00 | High-traffic applications |

⚠️ **Important**: Docker applications require minimum `small_3_0` (2GB RAM), recommended `medium_3_0` (4GB RAM)

### Database Configuration

**Local Database (on instance):**
```bash
export DATABASE_TYPE="mysql"        # or "postgresql"
export DB_EXTERNAL="false"
export DB_NAME="my_app_db"
```

**External RDS Database:**
```bash
export DATABASE_TYPE="postgresql"   # or "mysql"
export DB_EXTERNAL="true"
export DB_RDS_NAME="my-app-rds-db"
export DB_NAME="my_app_db"
```

**No Database:**
```bash
export DATABASE_TYPE="none"
```

### S3 Bucket Configuration

**Enable S3 Bucket:**
```bash
export ENABLE_BUCKET="true"
export BUCKET_NAME="my-app-storage-bucket"
export BUCKET_ACCESS="read_write"   # or "read_only"
export BUCKET_BUNDLE="small_1_0"    # 250GB storage
```

**Bucket Sizes:**
- `small_1_0` - 250GB storage, $3/month
- `medium_1_0` - 500GB storage, $5/month  
- `large_1_0` - 1TB storage, $10/month

## 📝 Complete Examples

### Example 1: LAMP Stack with PostgreSQL RDS

```bash
# Step 1: Create GitHub repository first
gh repo create my-lamp-application --private --description "LAMP stack with PostgreSQL RDS and S3 storage"

# Step 2: Clone and navigate
git clone https://github.com/YOUR_USERNAME/my-lamp-application.git
cd my-lamp-application

# Step 3: Download the script
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh
chmod +x setup-complete-deployment.sh

# Step 4: Configure for LAMP stack
export AUTO_MODE=true
export AWS_REGION="us-east-1"
export APP_TYPE="lamp"
export APP_NAME="My LAMP Application"
export INSTANCE_NAME="my-lamp-app-instance"
export BLUEPRINT_ID="ubuntu_22_04"
export BUNDLE_ID="small_3_0"
export DATABASE_TYPE="postgresql"
export DB_EXTERNAL="true"
export DB_RDS_NAME="my-lamp-postgres-db"
export DB_NAME="lamp_app_db"
export ENABLE_BUCKET="true"
export BUCKET_NAME="my-lamp-app-bucket"
export BUCKET_ACCESS="read_write"
export GITHUB_REPO="YOUR_USERNAME/my-lamp-application"  # ✅ Include username!
export REPO_VISIBILITY="private"

# Step 5: Run deployment setup
./setup-complete-deployment.sh --auto
```

### Example 2: Node.js API with Redis

```bash
# Step 1: Create GitHub repository
gh repo create nodejs-api-server --public --description "Node.js REST API with PostgreSQL and Redis"

# Step 2: Clone and setup
git clone https://github.com/YOUR_USERNAME/nodejs-api-server.git
cd nodejs-api-server
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh
chmod +x setup-complete-deployment.sh

# Step 3: Configure for Node.js
export AUTO_MODE=true
export AWS_REGION="us-west-2"
export APP_TYPE="nodejs"
export APP_NAME="Node.js API Server"
export INSTANCE_NAME="nodejs-api-server"
export BUNDLE_ID="small_3_0"
export DATABASE_TYPE="postgresql"
export DB_EXTERNAL="true"
export DB_RDS_NAME="nodejs-api-db"
export DB_NAME="api_db"
export GITHUB_REPO="YOUR_USERNAME/nodejs-api-server"  # ✅ Include username!
export REPO_VISIBILITY="public"

# Step 4: Run deployment setup
./setup-complete-deployment.sh --auto
```

### Example 3: Docker Application

```bash
# Step 1: Create GitHub repository
gh repo create docker-multi-service-app --private --description "Docker multi-service application with MySQL and S3"

# Step 2: Clone and setup
git clone https://github.com/YOUR_USERNAME/docker-multi-service-app.git
cd docker-multi-service-app
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh
chmod +x setup-complete-deployment.sh

# Step 3: Configure for Docker (requires more RAM)
export AUTO_MODE=true
export AWS_REGION="eu-west-1"
export APP_TYPE="docker"
export APP_NAME="Docker Multi-Service App"
export INSTANCE_NAME="docker-app-instance"
export BUNDLE_ID="medium_3_0"  # 4GB RAM for Docker
export DATABASE_TYPE="mysql"
export DB_EXTERNAL="false"     # Local MySQL in container
export ENABLE_BUCKET="true"
export BUCKET_NAME="docker-app-storage"
export GITHUB_REPO="YOUR_USERNAME/docker-multi-service-app"  # ✅ Include username!

# Step 4: Run deployment setup
./setup-complete-deployment.sh --auto
```

### Example 4: React Static Site

```bash
# Step 1: Create GitHub repository
gh repo create react-dashboard --public --description "React dashboard with NGINX static hosting"

# Step 2: Clone and setup
git clone https://github.com/YOUR_USERNAME/react-dashboard.git
cd react-dashboard
curl -O https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/setup-complete-deployment.sh
chmod +x setup-complete-deployment.sh

# Step 3: Configure for React
export AUTO_MODE=true
export AWS_REGION="us-east-1"
export APP_TYPE="react"
export APP_NAME="React Dashboard"
export INSTANCE_NAME="react-dashboard"
export BUNDLE_ID="micro_3_0"   # Smaller instance for static sites
export DATABASE_TYPE="none"    # No database needed
export GITHUB_REPO="YOUR_USERNAME/react-dashboard"  # ✅ Include username!
export REPO_VISIBILITY="public"

# Step 4: Run deployment setup
./setup-complete-deployment.sh --auto
```

## 🔄 What the Script Does

The setup script automatically performs these steps:

### 1. Prerequisites Check
- ✅ Verifies Git, GitHub CLI, and AWS CLI are installed
- ✅ Checks GitHub CLI authentication
- ✅ Validates AWS CLI configuration
- ✅ Confirms you're in a Git repository

### 2. GitHub Repository Setup
- ✅ Creates GitHub repository (if needed)
- ✅ Configures Git remote origin
- ✅ Sets repository visibility (public/private)
- ✅ Handles username/repository format for OIDC

### 3. AWS OIDC Configuration
- ✅ Creates GitHub OIDC provider in AWS (if needed)
- ✅ Creates IAM role for GitHub Actions
- ✅ Attaches necessary policies (ReadOnlyAccess + Custom Lightsail)
- ✅ Configures trust policy for your repository

### 4. File Generation
- ✅ Downloads reusable workflow from source repository
- ✅ Creates deployment configuration (`deployment-{type}.config.yml`)
- ✅ Creates GitHub Actions workflow (`.github/workflows/deploy-{type}.yml`)
- ✅ Generates example application (`example-{type}-app/`)

### 5. GitHub Integration
- ✅ Sets `AWS_ROLE_ARN` repository variable
- ✅ Commits all files to Git
- ✅ Pushes to GitHub to trigger first deployment

### 6. Validation
- ✅ Validates YAML syntax
- ✅ Checks required configuration sections
- ✅ Verifies workflow uses reusable deployment

## 📁 Generated Files

After running the script, you'll have these files in your repository:

```
your-repository/
├── .github/workflows/
│   ├── deploy-generic-reusable.yml    # Reusable workflow (downloaded)
│   └── deploy-{type}.yml              # Your app-specific workflow
├── deployment-{type}.config.yml       # Deployment configuration
├── example-{type}-app/                # Sample application
│   ├── index.php                      # (for LAMP)
│   ├── app.js                         # (for Node.js)
│   ├── app.py                         # (for Python)
│   ├── package.json                   # (for Node.js/React)
│   ├── docker-compose.yml             # (for Docker)
│   └── ...                           # Other app-specific files
└── README.md                          # (if created by script)
```

## 🚀 Deployment Process

Once files are pushed to GitHub, the deployment process automatically:

### Phase 1: Pre-Deployment (2-3 minutes)
1. **Instance Creation** - Creates Lightsail instance if needed
2. **System Updates** - Updates packages and installs dependencies
3. **Service Installation** - Installs Apache/NGINX, PHP, Node.js, Python, etc.
4. **Database Setup** - Configures local database or connects to RDS
5. **S3 Bucket** - Creates and attaches bucket (if enabled)

### Phase 2: Application Deployment (1-2 minutes)
1. **File Transfer** - Packages and transfers application files
2. **Environment Setup** - Creates environment variables and config files
3. **Permissions** - Sets proper file and directory permissions
4. **Service Configuration** - Configures web server and application services

### Phase 3: Post-Deployment (1-2 minutes)
1. **Service Restart** - Restarts all services with new configuration
2. **Health Checks** - Verifies application is responding
3. **Connectivity Tests** - Tests database and S3 connections
4. **Performance Optimization** - Applies caching and optimization settings

### Phase 4: Verification (30 seconds)
1. **Endpoint Testing** - Tests HTTP endpoints
2. **Service Status** - Verifies all services are running
3. **Final Report** - Generates deployment summary

**Total Time: 5-8 minutes** (varies by application complexity)

## 🔍 Monitoring Your Deployment

### GitHub Actions Dashboard
1. Go to your GitHub repository
2. Click the **Actions** tab
3. Select the latest workflow run
4. Monitor real-time progress and logs

### Deployment Status
The workflow provides detailed status updates:

```
🚀 Starting deployment...
✅ Instance created: your-app-instance
✅ Dependencies installed: Apache, PHP 8.3, PostgreSQL
✅ Database connected: RDS instance
✅ S3 bucket attached: your-app-bucket
✅ Application deployed successfully
🌐 Available at: http://your-instance-ip/
```

### Access Your Application
After successful deployment:
- **Main Application**: `http://your-instance-ip/`
- **Health Check**: `http://your-instance-ip/` (shows system info)
- **S3 File Manager**: `http://your-instance-ip/bucket-manager.php` (if bucket enabled)

## 🛠️ Customization

### Modifying Configuration

Edit `deployment-{type}.config.yml` to customize your deployment:

```yaml
# Example: Add Redis caching
dependencies:
  redis:
    enabled: true
    config:
      bind_all_interfaces: false

# Example: Add SSL certificates
ssl_certificates:
  enabled: true
  config:
    provider: "letsencrypt"
    domains:
      - "myapp.example.com"

# Example: Custom environment variables
application:
  environment_variables:
    APP_ENV: production
    API_KEY: "your-api-key"
    CACHE_DRIVER: redis
    SESSION_LIFETIME: 120
```

### Adding Custom Dependencies

The system supports many additional services:

```yaml
dependencies:
  # Caching
  memcached:
    enabled: true
  
  # Container support
  docker:
    enabled: true
    config:
      enable_compose: true
  
  # Version control
  git:
    enabled: true
    config:
      install_lfs: true
  
  # Security
  fail2ban:
    enabled: true
  
  # Monitoring
  htop:
    enabled: true
```

### Multiple Environments

Create separate configurations for different environments:

1. **Staging**: `deployment-staging.config.yml`
2. **Production**: `deployment-production.config.yml`

Update your workflow to use different configs per branch:

```yaml
jobs:
  deploy:
    uses: ./.github/workflows/deploy-generic-reusable.yml
    with:
      config_file: ${{ github.ref == 'refs/heads/main' && 'deployment-production.config.yml' || 'deployment-staging.config.yml' }}
```

## 🔐 Security Best Practices

### OIDC Authentication
The setup uses OpenID Connect (OIDC) for secure authentication:
- ✅ No long-lived AWS credentials stored in GitHub
- ✅ Temporary tokens (expire after ~1 hour)
- ✅ Repository-specific access control
- ✅ Branch-level restrictions

### IAM Permissions
The created IAM role has minimal required permissions:
- `ReadOnlyAccess` - For reading AWS resources
- Custom Lightsail policy - For managing Lightsail resources only

### Firewall Configuration
Automatic firewall setup:
```yaml
firewall:
  enabled: true
  config:
    allowed_ports:
      - "22"    # SSH
      - "80"    # HTTP
      - "443"   # HTTPS
    deny_all_other: true
```

### Database Security
- Secure password generation
- Connection encryption
- Network isolation for RDS

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. GitHub Repository Username Issues
**Error**: 
```
⚠️  GITHUB_REPO missing username, applying workaround before OIDC setup...
❌ Could not determine GitHub username from git remote
❌ OIDC setup will fail without username/repository format
💡 Please update MCP server to version 1.1.4+ or provide github_username parameter
```

**Root Cause**: The script needs the repository in `username/repository` format for OIDC setup, but only has the repository name.

**Solutions**:

**Option 1: Create Repository First (Recommended)**
```bash
# Create the GitHub repository first with proper naming
gh repo create reddit-app --private --description "reddit-app Node.js, MySQL, and AWS Lightsail deployment"

# Clone the repository
git clone https://github.com/YOUR_USERNAME/reddit-app.git
cd reddit-app

# Now run the setup script
export AUTO_MODE=true
export APP_TYPE="nodejs"
export APP_NAME="Reddit App"
export INSTANCE_NAME="reddit-app-instance"
export DATABASE_TYPE="mysql"
export GITHUB_REPO="YOUR_USERNAME/reddit-app"  # Include username!

./setup-complete-deployment.sh --auto
```

**Option 2: Set GITHUB_REPO with Username**
```bash
# If you know your GitHub username, include it in GITHUB_REPO
export GITHUB_REPO="your-github-username/your-repo-name"

# Example:
export GITHUB_REPO="john-doe/my-awesome-app"
```

**Option 3: Initialize Git Remote First**
```bash
# Initialize git and add remote before running script
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Now the script can detect the username from git remote
./setup-complete-deployment.sh
```

**Option 4: Manual Repository Creation**
```bash
# Create repository manually on GitHub.com, then:
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main

# Run setup script
./setup-complete-deployment.sh
```

**Verification Steps**:
After applying any solution, verify the setup:
```bash
# Check if git remote is properly configured
git remote -v
# Should show: origin  https://github.com/YOUR_USERNAME/YOUR_REPO.git (fetch)

# Verify GITHUB_REPO format
echo $GITHUB_REPO
# Should show: YOUR_USERNAME/YOUR_REPO (not just YOUR_REPO)

# Test GitHub CLI access
gh repo view
# Should show repository information without errors
```

**Prevention**: Always create your repository first using the recommended approach:
```bash
# ✅ Recommended workflow
gh repo create my-app --private --description "My application"
git clone https://github.com/YOUR_USERNAME/my-app.git
cd my-app
# Download and run setup script

# ❌ Avoid this workflow (causes username detection issues)
mkdir my-app && cd my-app
git init
# Download and run setup script (will fail OIDC setup)
```

#### 2. Authentication Errors
**Error**: `Error: Could not assume role with OIDC`

**Solution**:
```bash
# Check if AWS_ROLE_ARN is set
gh variable list

# Verify IAM role exists
aws iam get-role --role-name GitHubActions-YourApp-deployment

# Check trust policy
aws iam get-role --role-name GitHubActions-YourApp-deployment --query 'Role.AssumeRolePolicyDocument'
```

#### 2. Instance Creation Fails
**Error**: `Instance creation failed`

**Solutions**:
- Check AWS service limits in your region
- Verify you have permissions to create Lightsail instances
- Try a different availability zone
- Check if instance name is already taken

#### 3. Database Connection Issues
**Error**: `Database connection failed`

**Solutions**:
```bash
# For RDS issues
aws rds describe-db-instances --db-instance-identifier your-db-name

# Check security groups
aws rds describe-db-instances --db-instance-identifier your-db-name --query 'DBInstances[0].VpcSecurityGroups'

# Test connection from instance
ssh ubuntu@your-instance-ip
mysql -h your-rds-endpoint -u username -p
```

#### 4. S3 Bucket Issues
**Error**: `Bucket operations failed`

**Solutions**:
```bash
# Check if bucket exists
aws s3 ls s3://your-bucket-name/

# Verify bucket is attached to instance
aws lightsail get-bucket-access-keys --bucket-name your-bucket-name

# Test from instance
ssh ubuntu@your-instance-ip
aws s3 ls s3://your-bucket-name/
```

#### 5. Docker Deployment Issues
**Error**: `Docker build failed` or instance freezes

**Solutions**:
- Ensure instance has minimum 2GB RAM (`small_3_0` or larger)
- Use pre-built images from Docker Hub
- Check Docker Compose syntax
- Monitor memory usage during build

### Debug Commands

**Check deployment logs:**
```bash
# SSH into instance
ssh ubuntu@your-instance-ip

# Check service status
sudo systemctl status apache2  # or nginx, pm2, etc.

# View application logs
sudo tail -f /var/log/apache2/error.log
sudo tail -f /var/log/nginx/error.log

# Check deployment history
ls -la /var/backups/deployments/
```

**Verify configuration:**
```bash
# Check environment variables
cat /var/www/html/.env

# Verify database connection
php -r "new PDO('mysql:host=localhost;dbname=app_db', 'user', 'pass');"

# Test S3 access
aws s3 ls s3://your-bucket-name/
```

## 📞 Getting Help

### Documentation Resources
- **Main Repository**: [lamp-stack-lightsail](https://github.com/naveenraj44125-creator/lamp-stack-lightsail)
- **Issues**: [GitHub Issues](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/issues)
- **Examples**: Check `example-*-app` directories in the repository

### Support Channels
1. **GitHub Issues** - For bugs and feature requests
2. **GitHub Discussions** - For questions and community support
3. **Documentation** - Comprehensive guides in the repository

### Before Asking for Help
Please provide:
1. **Application type** (LAMP, Node.js, etc.)
2. **Configuration file** (`deployment-{type}.config.yml`)
3. **GitHub Actions logs** (from the Actions tab)
4. **Error messages** (exact text)
5. **AWS region** and instance details

## 🎉 Success! What's Next?

After successful deployment, you can:

### 1. Access Your Application
- Visit `http://your-instance-ip/` to see your application
- Use the S3 file manager at `http://your-instance-ip/bucket-manager.php`
- Monitor health at `http://your-instance-ip/health` (if available)

### 2. Set Up Custom Domain
```bash
# Point your domain to the instance IP
# Then update your configuration:
```

```yaml
ssl_certificates:
  enabled: true
  config:
    provider: "letsencrypt"
    domains:
      - "yourdomain.com"
      - "www.yourdomain.com"
```

### 3. Enable Monitoring
Add monitoring and alerting:

```yaml
monitoring:
  health_check:
    endpoint: "/health"
    expected_content: "OK"
    max_attempts: 10
    wait_between_attempts: 10
```

### 4. Scale Your Application
- Upgrade instance size in configuration
- Add load balancing for high traffic
- Implement database read replicas
- Set up CDN for static assets

### 5. Continuous Deployment
Your application now automatically deploys when you:
- Push to the `main` branch
- Merge pull requests
- Create releases

## 🏆 Conclusion

You now have a complete, production-ready deployment pipeline that:

- ✅ **Automatically deploys** your application on every push
- ✅ **Scales easily** with configuration changes
- ✅ **Includes monitoring** and health checks
- ✅ **Supports databases** (local or RDS)
- ✅ **Integrates S3 storage** for file uploads
- ✅ **Uses secure authentication** with OIDC
- ✅ **Provides detailed logging** and error reporting

Your deployment is now live and ready for production use! 🚀

---

*This guide is part of the [AWS Lightsail Automated Deployment System](https://github.com/naveenraj44125-creator/lamp-stack-lightsail). For more advanced features and examples, visit the main repository.*