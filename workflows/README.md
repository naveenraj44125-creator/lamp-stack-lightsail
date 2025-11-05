# AWS Lightsail Deployment Workflows

This directory contains Python scripts for deploying applications to AWS Lightsail instances with comprehensive logging and monitoring capabilities.

## 🚀 Quick Start

### Complete Deployment (Recommended)
```bash
# Deploy with all steps
python3 workflows/deploy.py --verify --cleanup --monitor

# Deploy to specific instance
python3 workflows/deploy.py --instance-name my-app --region us-west-2 --verify
```

### Individual Steps
```bash
# 1. Pre-deployment (install dependencies)
python3 workflows/deploy-pre-steps-generic.py

# 2. Create package
tar -czf app-package.tar.gz index.php css/ config/

# 3. Post-deployment (deploy application)
python3 workflows/deploy-post-steps-generic.py app-package.tar.gz --verify --cleanup

# 4. Monitor deployment
python3 workflows/deployment_monitor.py health
```

## 📁 File Structure

```
workflows/
├── deploy.py                      # 🎯 Main deployment orchestrator
├── deploy-pre-steps-generic.py    # 🔧 Pre-deployment (dependencies)
├── deploy-post-steps-generic.py   # 📦 Post-deployment (application)
├── deployment_monitor.py          # 🏥 Health monitoring
├── config_loader.py              # ⚙️  Configuration management
├── dependency_manager.py          # 📦 Dependency installation
├── lightsail_common.py           # 🔗 AWS Lightsail communication
├── lightsail_rds.py              # 🗄️  RDS database management
└── README.md                     # 📖 This file
```

## 🛠️ Core Scripts

### 1. `deploy.py` - Main Orchestrator
Complete deployment automation with enhanced logging.

**Features:**
- Orchestrates entire deployment process
- Creates deployment packages automatically
- Enhanced GitHub Actions logging
- Comprehensive error handling
- Deployment summary and next steps

**Usage:**
```bash
# Full deployment with monitoring
python3 workflows/deploy.py --verify --cleanup --monitor

# Skip pre-deployment (if dependencies already installed)
python3 workflows/deploy.py --skip-pre --verify

# Custom configuration
python3 workflows/deploy.py --config-file my-config.yml --instance-name my-app
```

### 2. `deploy-pre-steps-generic.py` - Dependency Installation
Installs and configures system dependencies based on configuration.

**Supported Dependencies:**
- **Web Servers:** Apache, Nginx
- **Databases:** MySQL, PostgreSQL (local or RDS)
- **Languages:** PHP, Python, Node.js
- **Caching:** Redis, Memcached
- **Tools:** Git, Docker, SSL certificates
- **Security:** Firewall (UFW)

**Usage:**
```bash
python3 workflows/deploy-pre-steps-generic.py --instance-name lamp-demo
```

### 3. `deploy-post-steps-generic.py` - Application Deployment
Deploys application files and configures services.

**Features:**
- Automatic service detection
- Backup creation before deployment
- Service-specific configuration
- Database setup (local or RDS)
- Performance optimization
- Deployment verification

**Usage:**
```bash
python3 workflows/deploy-post-steps-generic.py package.tar.gz --verify --cleanup
```

### 4. `deployment_monitor.py` - Health Monitoring
Comprehensive monitoring and troubleshooting tools.

**Commands:**
```bash
# System health check
python3 workflows/deployment_monitor.py health

# Monitor logs
python3 workflows/deployment_monitor.py logs --lines 100

# Restart services
python3 workflows/deployment_monitor.py restart apache2 mysql
```

## ⚙️ Configuration

### Configuration File: `deployment-generic.config.yml`

```yaml
# AWS Configuration
aws:
  region: us-east-1

# Lightsail Instance
lightsail:
  instance_name: lamp-stack-demo
  static_ip: ""

# Application Settings
application:
  name: "My LAMP Application"
  version: "1.0.0"
  type: web  # web, api, or custom
  php_version: "8.1"
  package_files:
    - index.php
    - css/
    - config/
  environment_variables:
    APP_ENV: production
    APP_DEBUG: false

# Dependencies to Install
dependencies:
  apache:
    enabled: true
    config:
      document_root: /var/www/html
      enable_rewrite: true
      hide_version: true
  
  mysql:
    enabled: true
    external: false  # Set to true for RDS
    config:
      create_app_database: true
      database_name: app_db
    # RDS configuration (if external: true)
    rds:
      database_name: my-rds-instance
      region: us-east-1
      master_database: app_db
  
  php:
    enabled: true
    version: "8.1"
    config:
      extensions: ["pdo", "pdo_mysql", "curl", "json", "mbstring"]
      enable_composer: true
  
  firewall:
    enabled: true
    config:
      allowed_ports: ["22", "80", "443"]

# Deployment Settings
deployment:
  timeouts:
    ssh_connection: 60
    command_execution: 300
  retries:
    max_attempts: 3
    ssh_connection: 5
  steps:
    pre_deployment:
      dependencies:
        enabled: true
    post_deployment:
      dependencies:
        enabled: true

# Health Check Configuration
monitoring:
  health_check:
    endpoint: "/"
    expected_content: "Hello"
    max_attempts: 10
    wait_between_attempts: 10
    initial_wait: 30
```

## 📊 GitHub Actions Integration

### Enhanced Logging Output

The workflows provide detailed logging perfect for GitHub Actions:

```bash
🚀 Starting generic application deployment
📦 Package File: app-package.tar.gz
🔍 Verify: True
🧹 Cleanup: True
📋 Application: My LAMP App v1.0.0
🏷️  Type: web
🌍 Instance: lamp-stack-demo
📍 Region: us-east-1

============================================================
📦 DEPLOYING APPLICATION FILES
============================================================
📤 Uploading package file app-package.tar.gz to remote instance...
🔧 Running: scp -i /tmp/key.pem...
   ✅ File copied successfully

🔧 Running: set -e
echo "Deploying application files to /var/www/html..."
   ✅ Success
   Deploying application files to /var/www/html...
   ✅ Backup created at /var/backups/app/20241105_143022
   ✅ Application files deployed successfully

============================================================
🔧 CONFIGURING APPLICATION
============================================================
🔧 Running: set -e
echo "Configuring Apache for application..."
   ✅ Success
   ✅ Apache configured for application

============================================================
🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!
============================================================
✅ Application: My LAMP App v1.0.0
🌐 Instance: lamp-stack-demo
📍 Region: us-east-1
🏷️  Type: web
```

### Sample GitHub Actions Workflow

```yaml
name: Deploy to Lightsail

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Deploy to Lightsail
      run: |
        python3 workflows/deploy.py \
          --instance-name lamp-stack-demo \
          --region us-east-1 \
          --verify \
          --cleanup \
          --monitor
```

## 🔧 Troubleshooting

### Common Issues

1. **SSH Connection Failures**
   ```bash
   # Check instance status
   python3 workflows/deployment_monitor.py health
   
   # Test connectivity
   aws lightsail get-instance --instance-name your-instance
   ```

2. **Service Start Failures**
   ```bash
   # Check service status
   python3 workflows/deployment_monitor.py health
   
   # Restart services
   python3 workflows/deployment_monitor.py restart
   ```

3. **Database Connection Issues**
   ```bash
   # Check database logs
   python3 workflows/deployment_monitor.py logs --lines 100
   
   # Test database connectivity manually
   ssh ubuntu@your-instance-ip
   mysql -u root -proot123 -e "SELECT 1;"
   ```

### Debug Mode

Enable verbose logging by setting environment variable:
```bash
export GITHUB_ACTIONS=true  # Enables verbose SSH logging
python3 workflows/deploy.py --verify
```

## 🚀 Advanced Usage

### Custom Dependency Installation

Add custom dependencies to `dependency_manager.py`:

```python
def _install_custom_tool(self, config: Dict[str, Any]) -> bool:
    """Install custom tool"""
    script = '''
    set -e
    echo "Installing custom tool..."
    # Your installation commands here
    '''
    success, output = self.client.run_command(script, timeout=180)
    return success
```

### RDS Integration

Configure external RDS database:

```yaml
dependencies:
  mysql:
    enabled: true
    external: true
    rds:
      database_name: my-rds-instance
      region: us-east-1
      master_database: app_db
      access_key: ${AWS_ACCESS_KEY_ID}
      secret_key: ${AWS_SECRET_ACCESS_KEY}
```

### Multi-Environment Support

Use different configuration files:

```bash
# Development
python3 workflows/deploy.py --config-file config/dev.yml

# Production
python3 workflows/deploy.py --config-file config/prod.yml
```

## 📈 Monitoring and Maintenance

### Regular Health Checks
```bash
# Daily health check
python3 workflows/deployment_monitor.py health

# Weekly log review
python3 workflows/deployment_monitor.py logs --lines 1000
```

### Performance Monitoring
The deployment automatically optimizes:
- Apache compression and caching
- PHP OPcache configuration
- System memory settings
- Log rotation

### Backup Strategy
Automatic backups are created:
- Application files: `/var/backups/app/YYYYMMDD_HHMMSS/`
- Database: Handled by dependency manager
- Configuration: Environment files preserved

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive logging to new features
4. Test with GitHub Actions
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.