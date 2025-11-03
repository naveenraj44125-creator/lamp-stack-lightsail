# Generic Application Deployment System for AWS Lightsail

A flexible, configuration-driven deployment system that supports multiple application stacks on AWS Lightsail.

## Overview

This system has evolved from a LAMP-specific deployment to a fully generic deployment solution that can handle various application types including:

- **Web Servers**: Apache, Nginx
- **Databases**: MySQL, PostgreSQL (local or RDS)
- **Languages**: PHP, Python, Node.js
- **Additional Services**: Redis, Memcached, Docker
- **Security**: Firewall, SSL certificates, monitoring

## Features

- **Configuration-Driven**: Simple `enabled: true/false` flags control the entire deployment stack
- **Modular Dependencies**: Each service is independent and reusable
- **AWS Integration**: Native support for Lightsail instances and RDS databases
- **GitHub Actions**: Automated CI/CD pipeline
- **Health Monitoring**: Comprehensive health checks and performance monitoring
- **Security**: Built-in security configurations and best practices

## Quick Start

1. **Configure your deployment** in `deployment-generic.config.yml`
2. **Set up GitHub Secrets** for AWS credentials
3. **Push to main branch** to trigger automatic deployment

## Configuration

The main configuration file `deployment-generic.config.yml` contains all deployment parameters:

```yaml
dependencies:
  apache:
    enabled: true
  mysql:
    enabled: true
    external: false  # Use local MySQL or set to true for RDS
  php:
    enabled: true
    version: "8.3"
```

## Project Structure

```
├── index.php                          # Main application file
├── config/
│   └── database.php                   # Database configuration
├── css/
│   └── style.css                      # Application styling
├── workflows/                         # Deployment scripts
│   ├── dependency_manager.py          # Manages service dependencies
│   ├── deploy-pre-steps-generic.py    # Pre-deployment steps
│   ├── deploy-post-steps-generic.py   # Post-deployment steps
│   ├── lightsail_common.py           # Common Lightsail operations
│   └── lightsail_rds.py              # RDS integration
├── deployment-generic.config.yml      # Main configuration
└── .github/workflows/                 # GitHub Actions workflows
```

## Deployment Process

1. **Pre-deployment**: System updates, dependency installation, service configuration
2. **Application Deployment**: File transfer, environment setup, permissions
3. **Post-deployment**: Service restart, optimization, health checks
4. **Verification**: Endpoint testing, performance validation

## Database Support

- **Local MySQL**: Automatically configured on the Lightsail instance
- **AWS RDS**: Connect to managed database service
- **PostgreSQL**: Alternative database option

## Security Features

- Firewall configuration with custom port rules
- SSL certificate support (Let's Encrypt)
- Secure file permissions
- Web server security headers
- Private key exclusion from repository

## Monitoring

- Health check endpoints
- Performance monitoring
- System resource tracking
- Deployment status reporting

## Version History

- **v3.0.0**: Complete transformation to generic deployment system
- **v2.x**: LAMP-specific deployment
- **v1.x**: Basic deployment scripts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the deployment
5. Submit a pull request

## License

This project is licensed under the MIT License.
