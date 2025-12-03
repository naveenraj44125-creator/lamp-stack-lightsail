# AWS Lightsail Automated Deployment System

A complete, production-ready deployment automation system for AWS Lightsail with GitHub Actions. Deploy LAMP, Node.js, Python, React, and NGINX applications with a single command.

## 🚀 Quick Start

### For New Projects

Create a new repository with automated deployment:

```bash
./setup-new-repo.sh
```

### For Existing Projects

Add deployment automation to your existing repository:

```bash
cd /path/to/your/repo
./integrate-lightsail-actions.sh
```

Or download and run:

```bash
curl -sL https://raw.githubusercontent.com/naveenraj44125-creator/lamp-stack-lightsail/main/integrate-lightsail-actions.sh | bash
```

## ✨ Features

### 🎯 One-Command Setup
- **Automated OIDC Configuration** - Creates IAM roles and policies automatically
- **GitHub Integration** - Sets up workflows and variables
- **Interactive Wizard** - Guides you through configuration
- **Zero Manual Steps** - Everything configured automatically

### 🛠️ Supported Application Types
- **LAMP Stack** - Apache + PHP + MySQL/PostgreSQL
- **NGINX** - Static sites and reverse proxy
- **Node.js** - Express, Next.js, NestJS, APIs
- **Python** - Flask, Django, FastAPI
- **React** - CRA, Vite, Next.js static exports
- **🐳 Docker** - Multi-container applications with Docker Compose

### 🗄️ Database Support
- **Local Installation** - MySQL or PostgreSQL on instance
- **AWS RDS Integration** - Managed database service
- **Automatic Configuration** - Connection strings and credentials
- **Migration Support** - Database initialization scripts

### 🪣 S3 Bucket Integration
- **Automatic Creation** - Buckets created if they don't exist
- **Instance Attachment** - Credentials configured automatically
- **Access Control** - Read-only or read-write permissions
- **Multiple Sizes** - 250GB, 500GB, or 1TB storage options
- **Web Interface** - Upload/download files via browser

### 🔐 Security & Authentication
- **OIDC Authentication** - No long-lived credentials needed
- **IAM Role Management** - Proper least-privilege policies
- **Firewall Configuration** - Automatic port management
- **SSL Support** - Let's Encrypt integration ready

### 📊 Monitoring & Health Checks
- **Deployment Verification** - Automatic health checks
- **Service Monitoring** - Status tracking for all services
- **Performance Metrics** - Response time and resource usage
- **Detailed Logging** - Complete deployment audit trail

## 📖 Complete Example: LAMP Stack Deployment

Let's walk through deploying a LAMP stack application from scratch.

### Step 1: Create New Repository

```bash
./setup-new-repo.sh
```

The interactive wizard will ask:

```
Repository name: my-lamp-app
Application type: 1 (LAMP Stack)
AWS Region: 1 (us-east-1)
Database: 3 (PostgreSQL)
Use RDS: y
RDS instance name: my-lamp-db
Database name: app_db
Enable bucket: y
Bucket name: my-lamp-bucket
Bucket access: 2 (read_write)
Bucket size: 1 (small - 250GB)
```

### Step 2: Automatic Setup

The script automatically:
- ✅ Creates GitHub repository
- ✅ Sets up OIDC provider in AWS
- ✅ Creates IAM role with policies
- ✅ Configures GitHub variables
- ✅ Generates deployment config
- ✅ Copies workflow files
- ✅ Pushes initial commit

### Step 3: Deployment Configuration

The generated `deployment-lamp.config.yml`:

```yaml
lightsail:
  instance_name: "my-lamp-app"
  bucket:
    enabled: true
    name: "my-lamp-bucket"
    access_level: "read_write"
    bundle_id: "small_1_0"

dependencies:
  apache:
    enabled: true
    config:
      document_root: "/var/www/html"
      enable_rewrite: true
  
  php:
    enabled: true
    version: "8.3"
    config:
      extensions:
        - "pgsql"      # PostgreSQL driver
        - "curl"       # HTTP client
        - "mbstring"   # String handling
        - "xml"        # XML support
        - "zip"        # Archive support
        - "redis"      # Redis client
      enable_composer: true
  
  postgresql:
    enabled: true
    external: true
    rds:
      database_name: "my-lamp-db"
      region: "us-east-1"
      master_database: "app_db"
  
  redis:
    enabled: true
    config:
      bind_all_interfaces: false
  
  git:
    enabled: true
  
  firewall:
    enabled: true
    config:
      allowed_ports:
        - "22"    # SSH
        - "80"    # HTTP
        - "443"   # HTTPS
```

### Step 4: Customize Dependencies

Want to add more services? Just edit the config:

```yaml
dependencies:
  # Add Memcached
  memcached:
    enabled: true
    version: "latest"
  
  # Add Docker
  docker:
    enabled: true
    config:
      enable_compose: true
  
  # Enable SSL
  ssl_certificates:
    enabled: true
    config:
      provider: "letsencrypt"
      domains:
        - "myapp.example.com"
```

### Step 5: Deploy

Push to trigger deployment:

```bash
git add .
git commit -m "Update configuration"
git push origin main
```

GitHub Actions automatically:
1. ✅ Creates Lightsail instance (if needed)
2. ✅ Installs Apache, PHP 8.3, PostgreSQL client
3. ✅ Configures Redis cache
4. ✅ Creates S3 bucket
5. ✅ Attaches bucket to instance
6. ✅ Connects to RDS database
7. ✅ Deploys application files
8. ✅ Configures firewall
9. ✅ Runs health checks

### Step 6: Access Your Application

After deployment (5-10 minutes):

```
Application: http://your-instance-ip/
Bucket Manager: http://your-instance-ip/bucket-manager.php
Health Status: http://your-instance-ip/
```

## 🔧 Dependency Selection Guide

### Available Dependencies

All dependencies are controlled by simple `enabled: true/false` flags:

#### Web Servers
```yaml
dependencies:
  apache:
    enabled: true
    version: "latest"
    config:
      document_root: "/var/www/html"
      enable_ssl: false
      enable_rewrite: true
  
  nginx:
    enabled: false  # Can't use both Apache and NGINX
    version: "latest"
    config:
      document_root: "/var/www/html"
```

#### Programming Languages
```yaml
  php:
    enabled: true
    version: "8.3"
    config:
      extensions:
        - "pgsql"      # PostgreSQL
        - "mysql"      # MySQL (if using MySQL)
        - "curl"
        - "mbstring"
        - "xml"
        - "zip"
        - "redis"
      enable_composer: true
  
  python:
    enabled: false
    version: "3.9"
    config:
      pip_packages:
        - "flask"
        - "gunicorn"
      virtual_env: true
  
  nodejs:
    enabled: false
    version: "18"
    config:
      npm_packages:
        - "pm2"
      package_manager: "npm"  # or "yarn"
```

#### Databases
```yaml
  mysql:
    enabled: false
    external: false  # true for RDS
    rds:
      database_name: "my-rds-instance"
      region: "us-east-1"
      master_database: "app_db"
  
  postgresql:
    enabled: true
    external: true  # Using RDS
    rds:
      database_name: "my-postgres-db"
      region: "us-east-1"
      master_database: "app_db"
```

#### Caching & Additional Services
```yaml
  redis:
    enabled: true
    version: "latest"
    config:
      bind_all_interfaces: false
  
  memcached:
    enabled: false
    version: "latest"
  
  docker:
    enabled: false
    version: "latest"
    config:
      enable_compose: true
```

#### System Services
```yaml
  git:
    enabled: true
    config:
      install_lfs: false
  
  firewall:
    enabled: true
    config:
      allowed_ports:
        - "22"    # SSH
        - "80"    # HTTP
        - "443"   # HTTPS
      deny_all_other: true
  
  ssl_certificates:
    enabled: false
    config:
      provider: "letsencrypt"
      domains:
        - "example.com"
```

### Common Dependency Combinations

#### LAMP Stack (Linux, Apache, MySQL, PHP)
```yaml
dependencies:
  apache: { enabled: true }
  php: { enabled: true, version: "8.3" }
  mysql: { enabled: true, external: false }
  redis: { enabled: true }
  git: { enabled: true }
  firewall: { enabled: true }
```

#### LEMP Stack (Linux, NGINX, MySQL, PHP)
```yaml
dependencies:
  nginx: { enabled: true }
  php: { enabled: true, version: "8.3" }
  mysql: { enabled: true, external: false }
  redis: { enabled: true }
  git: { enabled: true }
  firewall: { enabled: true }
```

#### Node.js API Server
```yaml
dependencies:
  nodejs: { enabled: true, version: "18" }
  postgresql: { enabled: true, external: true }
  redis: { enabled: true }
  git: { enabled: true }
  firewall: { enabled: true }
```

#### Python Web Application
```yaml
dependencies:
  python: { enabled: true, version: "3.9" }
  nginx: { enabled: true }
  postgresql: { enabled: true, external: true }
  redis: { enabled: true }
  git: { enabled: true }
  firewall: { enabled: true }
```

#### Static Site (React/Vue/Angular)
```yaml
dependencies:
  nginx: { enabled: true }
  nodejs: { enabled: true }  # For build process
  git: { enabled: true }
  firewall: { enabled: true }
```

## 📁 Project Structure

```
lamp-stack-lightsail/
├── 🔧 Setup Scripts
│   ├── setup-new-repo.sh              # Create new repository with deployment
│   ├── integrate-lightsail-actions.sh # Add to existing repository
│   └── setup-github-oidc.sh           # Manual OIDC setup (if needed)
│
├── 📋 Configuration
│   ├── deployment-lamp-stack.config.yml
│   ├── deployment-nginx.config.yml
│   ├── deployment-nodejs.config.yml
│   ├── deployment-python.config.yml
│   └── deployment-react.config.yml
│
├── 🤖 GitHub Actions Workflows
│   └── .github/workflows/
│       ├── deploy-generic-reusable.yml  # Main deployment engine
│       └── aws-deploy.yml               # Workflow trigger
│
├── 🐍 Deployment Automation
│   └── workflows/
│       ├── config_loader.py             # Configuration parser
│       ├── dependency_manager.py        # Service installation
│       ├── deploy-pre-steps-generic.py  # Pre-deployment tasks
│       ├── deploy-post-steps-generic.py # Post-deployment tasks
│       ├── deployment_monitor.py        # Health checks
│       ├── lightsail_common.py          # Lightsail operations
│       ├── lightsail_rds.py             # RDS integration
│       ├── lightsail_bucket.py          # S3 bucket management
│       └── view_command_log.py          # Logging utilities
│
├── 📱 Example Applications
│   ├── example-lamp-app/
│   │   ├── index.php
│   │   ├── bucket-manager.php           # S3 file manager
│   │   ├── bucket-demo.php              # S3 usage examples
│   │   ├── config/database.php
│   │   └── config/cache.php
│   ├── example-nginx-app/
│   ├── example-nodejs-app/
│   ├── example-python-app/
│   ├── example-react-app/
│   ├── 🐳 example-docker-app/           # Basic Docker LAMP stack
│   └── 🐳 example-recipe-docker-app/    # Recipe Manager with S3
│
└── 📚 Documentation
    ├── README.md                        # This file
    ├── INTEGRATION-GUIDE.md             # Integration documentation
    ├── BUCKET-INTEGRATION.md            # S3 bucket guide
    ├── DOCKER-DEPLOYMENT-GUIDE.md       # Docker deployment guide
    ├── DOCKER-EXAMPLES-GUIDE.md         # Docker examples comparison
    ├── GITHUB-ACTIONS-OIDC-GUIDE.md     # OIDC setup guide
    └── REUSABLE_WORKFLOWS.md            # Workflow documentation
```

## 🔄 Deployment Process

### Automatic Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. Push to GitHub (main branch)                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. GitHub Actions Triggered                                │
│     • Checkout code                                         │
│     • Configure AWS credentials (OIDC)                      │
│     • Load deployment configuration                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Pre-Deployment Steps                                    │
│     • Update system packages                                │
│     • Install dependencies (Apache, PHP, etc.)              │
│     • Configure services                                    │
│     • Set up database connections                           │
│     • Create S3 bucket (if enabled)                         │
│     • Attach bucket to instance                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Application Deployment                                  │
│     • Package application files                             │
│     • Transfer to Lightsail instance                        │
│     • Extract and set permissions                           │
│     • Create environment files                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Post-Deployment Steps                                   │
│     • Configure web server                                  │
│     • Set up database schema                                │
│     • Restart services                                      │
│     • Clear caches                                          │
│     • Optimize performance                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  6. Health Checks & Verification                            │
│     • Test HTTP endpoints                                   │
│     • Verify service status                                 │
│     • Check database connectivity                           │
│     • Validate bucket access                                │
│     • Generate deployment report                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  7. Deployment Complete ✅                                   │
│     • Application accessible                                │
│     • Monitoring active                                     │
│     • Logs available in GitHub Actions                      │
└─────────────────────────────────────────────────────────────┘
```

## 🪣 S3 Bucket Integration

### Automatic Bucket Setup

When enabled, the system automatically:
1. Creates Lightsail bucket (if doesn't exist)
2. Attaches bucket to instance with credentials
3. Configures access permissions
4. Deploys web-based file manager

### Configuration

```yaml
lightsail:
  bucket:
    enabled: true
    name: "my-app-bucket"
    access_level: "read_write"  # or "read_only"
    bundle_id: "small_1_0"      # 250GB storage
```

### Bucket Sizes

| Bundle ID | Storage | Transfer/Month | Use Case |
|-----------|---------|----------------|----------|
| small_1_0 | 250GB | 100GB | Small apps, testing |
| medium_1_0 | 500GB | 250GB | Medium apps, production |
| large_1_0 | 1TB | 500GB | Large apps, heavy usage |

### Using the Bucket

**Web Interface:**
- Upload files: `http://your-ip/bucket-manager.php`
- View examples: `http://your-ip/bucket-demo.php`

**AWS CLI:**
```bash
# List files
aws s3 ls s3://my-app-bucket/

# Upload file
aws s3 cp file.txt s3://my-app-bucket/

# Download file
aws s3 cp s3://my-app-bucket/file.txt ./
```

**PHP Code:**
```php
use Aws\S3\S3Client;

$s3 = new S3Client([
    'version' => 'latest',
    'region'  => 'us-east-1'
]);

// Upload
$s3->putObject([
    'Bucket' => 'my-app-bucket',
    'Key'    => 'uploads/photo.jpg',
    'Body'   => fopen('photo.jpg', 'r')
]);
```

## 🔐 AWS Authentication (OIDC)

### Automatic Setup

Both `setup-new-repo.sh` and `integrate-lightsail-actions.sh` automatically:

1. **Create OIDC Provider** (if doesn't exist)
   ```
   URL: token.actions.githubusercontent.com
   Audience: sts.amazonaws.com
   ```

2. **Create IAM Role**
   ```
   Name: GitHubActionsRole-{instance-name}
   Trust: repo:{owner}/{repo}:ref:refs/heads/main
   ```

3. **Attach Policies**
   - `ReadOnlyAccess` (AWS managed)
   - Custom Lightsail policy (full access)

4. **Set GitHub Variable**
   ```
   AWS_ROLE_ARN: arn:aws:iam::123456789:role/GitHubActionsRole-...
   ```

### Manual Setup (if needed)

If automatic setup fails, run:

```bash
./setup-github-oidc.sh
```

Or follow: [GITHUB-ACTIONS-OIDC-GUIDE.md](GITHUB-ACTIONS-OIDC-GUIDE.md)

## 🔍 Monitoring & Troubleshooting

### View Deployment Logs

1. Go to GitHub repository
2. Click "Actions" tab
3. Select latest workflow run
4. View step-by-step logs

### Check Instance Status

```bash
# SSH into instance
ssh ubuntu@your-instance-ip

# Check service status
sudo systemctl status apache2
sudo systemctl status redis-server

# View logs
sudo tail -f /var/log/apache2/error.log
```

### Verify Bucket Integration

```bash
# On the instance
./verify-bucket-integration.sh
```

### Common Issues

**Deployment fails with "Access Denied"**
- Check AWS_ROLE_ARN is set in GitHub variables
- Verify IAM role has proper permissions
- Ensure trust policy includes your repository

**Database connection fails**
- Verify RDS instance is running
- Check security group allows connections
- Confirm DB credentials in GitHub secrets

**Bucket operations fail**
- Verify bucket is attached to instance
- Check access level (read_only vs read_write)
- Ensure AWS CLI is installed on instance

## 📊 Comparison: setup-new-repo.sh vs integrate-lightsail-actions.sh

| Feature | setup-new-repo.sh | integrate-lightsail-actions.sh |
|---------|-------------------|--------------------------------|
| **Use Case** | Create new repository | Add to existing repository |
| **Git Init** | ✅ Creates new repo | ❌ Uses existing |
| **GitHub Repo** | ✅ Creates on GitHub | ❌ Uses existing |
| **Example App** | ✅ Includes sample code | ❌ Uses your code |
| **Workflows** | ✅ Copies from template | ✅ Downloads/copies |
| **Config** | ✅ Generates | ✅ Generates |
| **OIDC Setup** | ✅ Automatic | ✅ Automatic |
| **GitHub Variables** | ✅ Sets automatically | ✅ Sets automatically |
| **Initial Push** | ✅ Pushes to GitHub | ❌ You push manually |
| **Best For** | Starting from scratch | Existing projects |

Both scripts provide identical deployment capabilities!

## 🎓 Advanced Usage

### Custom Environment Variables

```yaml
application:
  environment_variables:
    APP_ENV: production
    API_KEY: "your-key"
    CACHE_DRIVER: redis
    SESSION_LIFETIME: 120
```

### Multiple Environments

Create separate configs:
- `deployment-staging.config.yml`
- `deployment-production.config.yml`

Update workflow to use different configs per branch.

### Custom Deployment Steps

```yaml
deployment:
  steps:
    post_deployment:
      common:
        enabled: true
        verify_extraction: true
        create_env_file: true
        cleanup_temp_files: true
      dependencies:
        enabled: true
        configure_application: true
        set_permissions: true
        restart_services: true
```

### Health Check Configuration

```yaml
monitoring:
  health_check:
    endpoint: "/health"
    expected_content: "OK"
    max_attempts: 10
    wait_between_attempts: 10
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - Feel free to use and modify for your projects.

## 🆘 Support

- **Documentation**: See guides in repository
- **Issues**: [GitHub Issues](https://github.com/naveenraj44125-creator/lamp-stack-lightsail/issues)
- **Examples**: Check `example-*-app` directories

## 🐳 Docker Deployment Examples

Two complete Docker examples demonstrating containerized deployments:

### 1. Basic Docker LAMP Stack (`example-docker-app/`)
**Perfect for learning Docker basics**

- Multi-container architecture (Apache, MySQL, Redis, phpMyAdmin)
- Service health monitoring dashboard
- Container networking demonstration
- Persistent data volumes
- Quick deployment testing

```bash
cd example-docker-app
docker-compose up -d
open http://localhost
```

### 2. Recipe Manager with S3 (`example-recipe-docker-app/`)
**Production-ready application with AWS integration**

- Complete recipe management system
- Admin panel with authentication
- Image upload to AWS Lightsail buckets
- RESTful API with CRUD operations
- Session management with Redis
- Responsive modern UI

```bash
cd example-recipe-docker-app
cp .env.example .env
# Edit .env with your bucket name
docker-compose up -d
open http://localhost
open http://localhost/admin/  # admin/admin123
```

**Features Demonstrated**:
- ✅ Docker Compose orchestration
- ✅ AWS S3 bucket integration
- ✅ File upload handling
- ✅ Database relationships
- ✅ Authentication & sessions
- ✅ RESTful API design
- ✅ Production deployment patterns

**Deployment**: Use `deployment-docker.config.yml` or `deployment-recipe-docker.config.yml`

📚 **Learn More**: 
- [Docker Deployment Guide](DOCKER-DEPLOYMENT-GUIDE.md)
- [Docker Examples Comparison](DOCKER-EXAMPLES-GUIDE.md)

---

## 🎉 Success Stories

This system successfully deploys:
- ✅ LAMP applications with PostgreSQL RDS
- ✅ Node.js APIs with Redis caching
- ✅ Python web apps with S3 storage
- ✅ React SPAs with NGINX
- ✅ Multi-service applications with Docker
- ✅ Containerized apps with S3 integration

Ready to deploy? Run `./setup-new-repo.sh` or `./integrate-lightsail-actions.sh` now! 🚀
