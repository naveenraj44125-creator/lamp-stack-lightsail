# Generic Application Deployment System

This guide explains how to use the new generic deployment system that can deploy any type of application with configurable dependencies.

## Overview

The generic deployment system replaces the LAMP-specific workflow with a flexible, configuration-driven approach that supports:

- **Multiple Application Types**: Web applications, APIs, static sites, custom applications
- **Configurable Dependencies**: Apache, Nginx, MySQL, PostgreSQL, PHP, Python, Node.js, Redis, Docker, and more
- **Simple Yes/No Configuration**: Each dependency can be enabled or disabled with a simple boolean flag
- **Automatic Installation**: Dependencies are automatically installed and configured based on your configuration
- **Language-Specific Testing**: Automatic testing based on enabled dependencies

## Quick Start

1. **Copy the generic configuration file**:
   ```bash
   cp deployment-generic.config.yml deployment.config.yml
   ```

2. **Configure your application** by editing `deployment.config.yml`:
   - Set your application details
   - Enable/disable dependencies as needed
   - Configure AWS and Lightsail settings

3. **Use the generic workflow**:
   ```bash
   cp .github/workflows/deploy-generic.yml .github/workflows/deploy.yml
   ```

4. **Commit and push** - the workflow will automatically deploy based on your configuration!

## Configuration Structure

### Application Configuration

```yaml
application:
  name: my-app
  version: "1.0.0"
  type: web  # web, api, static, custom
  
  package_files:
    - "index.php"
    - "css/"
    - "config/"
  
  package_fallback: true
  
  environment_variables:
    APP_ENV: production
    APP_DEBUG: false
```

### Dependencies Configuration

Each dependency can be enabled/disabled with simple boolean flags:

```yaml
dependencies:
  # Web Servers
  apache:
    enabled: true    # Set to false to disable
    version: "latest"
    config:
      document_root: "/var/www/html"
      enable_ssl: false
      enable_rewrite: true
  
  nginx:
    enabled: false   # Not needed if using Apache
  
  # Databases
  mysql:
    enabled: true
    version: "8.0"
    config:
      create_app_database: true
      database_name: "app_db"
  
  postgresql:
    enabled: false   # Alternative to MySQL
  
  # Programming Languages
  php:
    enabled: true
    version: "8.1"
    config:
      extensions:
        - "pdo"
        - "pdo_mysql"
        - "curl"
      enable_composer: true
  
  python:
    enabled: false   # Enable for Python apps
    version: "3.9"
    config:
      pip_packages:
        - "flask"
        - "gunicorn"
      virtual_env: true
  
  nodejs:
    enabled: false   # Enable for Node.js apps
    version: "18"
    config:
      npm_packages:
        - "express"
        - "pm2"
  
  # Additional Services
  redis:
    enabled: false
  
  docker:
    enabled: false
  
  git:
    enabled: true    # Usually needed
  
  firewall:
    enabled: true    # Recommended for security
    config:
      allowed_ports:
        - "22"    # SSH
        - "80"    # HTTP
        - "443"   # HTTPS
```

## Application Types

### Web Applications (`type: web`)
- Deploys to `/var/www/html`
- Configures web server (Apache/Nginx)
- Sets `www-data` ownership
- Supports PHP, Python (WSGI), static files

### API Applications (`type: api`)
- Deploys to `/opt/app` or `/opt/nodejs-app`
- Creates systemd services for Python/Node.js
- Sets `ubuntu` user ownership
- Configures service auto-start

### Static Sites (`type: static`)
- Deploys to web server document root
- Optimized for static file serving
- No backend language configuration

### Custom Applications (`type: custom`)
- Flexible deployment location
- Minimal assumptions about structure
- Allows custom configuration

## Supported Dependencies

### Web Servers
- **Apache**: Full-featured web server with mod_rewrite, security headers
- **Nginx**: High-performance web server with PHP-FPM support

### Databases
- **MySQL**: Popular relational database with automatic setup
- **PostgreSQL**: Advanced relational database
- **Redis**: In-memory data store for caching
- **Memcached**: Distributed memory caching

### Programming Languages
- **PHP**: With configurable extensions and Composer
- **Python**: With virtual environments and pip packages
- **Node.js**: With npm/yarn and global packages

### Additional Tools
- **Docker**: Container platform with Docker Compose
- **Git**: Version control with optional Git LFS
- **Firewall**: UFW configuration with custom ports
- **SSL Certificates**: Let's Encrypt integration
- **Monitoring**: System monitoring tools

## Example Configurations

### LAMP Stack (PHP Web Application)
```yaml
application:
  type: web
dependencies:
  apache:
    enabled: true
  mysql:
    enabled: true
  php:
    enabled: true
  git:
    enabled: true
  firewall:
    enabled: true
```

### Python Flask API
```yaml
application:
  type: api
dependencies:
  python:
    enabled: true
    config:
      pip_packages:
        - "flask"
        - "gunicorn"
  postgresql:
    enabled: true
  redis:
    enabled: true
  git:
    enabled: true
  firewall:
    enabled: true
```

### Node.js Application
```yaml
application:
  type: web
dependencies:
  nginx:
    enabled: true
  nodejs:
    enabled: true
    config:
      npm_packages:
        - "express"
        - "pm2"
  mysql:
    enabled: true
  git:
    enabled: true
  firewall:
    enabled: true
```

### Static Website
```yaml
application:
  type: static
dependencies:
  nginx:
    enabled: true
  git:
    enabled: true
  firewall:
    enabled: true
  ssl_certificates:
    enabled: true
```

## Workflow Features

### Automatic Testing
The workflow automatically sets up testing based on enabled dependencies:

- **PHP**: Syntax validation, local server testing
- **Python**: Syntax checking, requirements installation
- **Node.js**: Package installation, test script execution
- **Generic**: Configuration validation, file structure checks

### Dependency Installation
Dependencies are installed in the correct order:
1. System tools (Git, Firewall)
2. Web servers (Apache, Nginx)
3. Databases (MySQL, PostgreSQL)
4. Programming languages (PHP, Python, Node.js)
5. Additional services (Redis, Docker)

### Service Configuration
- Automatic service startup configuration
- Security hardening (firewall, headers)
- Performance optimization
- Log rotation setup

### Deployment Verification
- Health checks based on application type
- External connectivity testing
- Performance and security validation
- Comprehensive deployment summary

## Migration from LAMP-Specific Workflow

To migrate from the old LAMP-specific workflow:

1. **Copy the generic configuration**:
   ```bash
   cp deployment-generic.config.yml deployment.config.yml
   ```

2. **Update your configuration** to match your current LAMP setup:
   ```yaml
   dependencies:
     apache:
       enabled: true
     mysql:
       enabled: true
     php:
       enabled: true
     git:
       enabled: true
     firewall:
       enabled: true
   ```

3. **Replace the workflow file**:
   ```bash
   cp .github/workflows/deploy-generic.yml .github/workflows/deploy.yml
   ```

4. **Test the deployment** - it should work exactly like before but with more flexibility!

## Advanced Configuration

### Custom Dependency Versions
```yaml
dependencies:
  php:
    enabled: true
    version: "8.2"  # Specific version
  mysql:
    enabled: true
    version: "8.0"  # Specific version
```

### Custom Package Files
```yaml
application:
  package_files:
    - "src/"
    - "public/"
    - "composer.json"
    - "package.json"
  package_fallback: false  # Strict file inclusion
```

### Environment-Specific Configuration
```yaml
application:
  environment_variables:
    APP_ENV: production
    DATABASE_URL: "mysql://user:pass@localhost/db"
    REDIS_URL: "redis://localhost:6379"
```

### Security Configuration
```yaml
dependencies:
  firewall:
    enabled: true
    config:
      allowed_ports:
        - "22"
        - "80"
        - "443"
        - "3000"  # Custom application port
      deny_all_other: true
  
  ssl_certificates:
    enabled: true
    config:
      provider: "letsencrypt"
      domains:
        - "example.com"
        - "www.example.com"
```

## Troubleshooting

### Common Issues

1. **Dependency Installation Fails**
   - Check the GitHub Actions logs for specific error messages
   - Verify the dependency configuration is correct
   - Some dependencies may conflict (e.g., Apache + Nginx)

2. **Application Not Accessible**
   - Verify firewall configuration allows HTTP/HTTPS
   - Check that the web server is enabled and configured
   - Ensure application files are in the correct location

3. **Database Connection Issues**
   - Verify database dependency is enabled
   - Check database configuration in your application
   - Default credentials: root/root123 for MySQL

### Debugging

Enable verbose logging by adding to your configuration:
```yaml
monitoring:
  logging:
    level: DEBUG
    include_timestamps: true
```

### Getting Help

1. Check the GitHub Actions workflow logs
2. Review the deployment summary in the Actions tab
3. Verify your configuration against the examples
4. Test locally using the Python scripts directly

## Benefits of the Generic System

1. **Flexibility**: Support any application type with any combination of dependencies
2. **Simplicity**: Just enable/disable dependencies with boolean flags
3. **Consistency**: Same workflow works for all application types
4. **Maintainability**: Single codebase instead of multiple LAMP-specific scripts
5. **Extensibility**: Easy to add new dependencies and application types
6. **Testing**: Automatic language-specific testing based on configuration
7. **Documentation**: Self-documenting through configuration structure

The generic deployment system provides all the power of the original LAMP workflow while being flexible enough to handle any application stack you need!
