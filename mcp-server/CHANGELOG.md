# Changelog

All notable changes to the Lightsail Deployment MCP Server will be documented in this file.

## [1.0.0] - 2025-12-07

### Added
- Initial release of Lightsail Deployment MCP Server
- `setup_new_repository` tool for creating new repos with deployment automation
- `integrate_existing_repository` tool for adding deployment to existing projects
- `generate_deployment_config` tool for creating configuration files
- `setup_oidc_authentication` tool for AWS authentication setup
- `get_deployment_status` tool for monitoring deployments
- `list_available_examples` tool for discovering application templates
- Support for 6 application types: LAMP, NGINX, Node.js, Python, React, Docker
- S3 bucket integration support
- RDS database integration support
- Comprehensive documentation and installation guides

### Features
- Automatic OIDC configuration generation
- Interactive deployment config creation
- GitHub Actions workflow integration
- Health check monitoring
- Multi-region support
- Database migration support
- Docker Compose orchestration

### Documentation
- Complete README with usage examples
- Installation guide for multiple MCP clients
- Troubleshooting guide
- API documentation for all tools

## [1.2.0] - 2025-12-07

### Added
- **HTTP/SSE Server Mode**: Deploy MCP server as HTTP endpoint on Lightsail
- `server.js` for running as HTTP service with SSE transport
- Token-based authentication for secure remote access
- Automated deployment script (`deploy-to-lightsail.sh`)
- Systemd service configuration for production deployment
- NGINX reverse proxy configuration with SSL support
- Complete deployment guide (DEPLOY.md)
- Health check endpoint for monitoring
- Support for remote team access

### Improved
- Multiple installation options (Remote, NPX, Global, Local)
- Better documentation for deployment scenarios
- Production-ready configuration examples

## [1.1.0] - 2025-12-07

### Added
- `diagnose_deployment` tool for automated troubleshooting
- Comprehensive TROUBLESHOOTING.md guide
- Diagnostic checks for prerequisites, GitHub, AWS, configuration, and instances
- Automated issue detection and recommendations
- Support for targeted diagnostic checks (prerequisites, configuration, github, aws, instance)

### Improved
- Enhanced error messages with actionable solutions
- Better documentation with troubleshooting examples
- Test suite now validates all 7 tools

## [Unreleased]

### Planned Features
- Rollback support for failed deployments
- Blue-green deployment strategies
- Automatic scaling configuration
- Cost estimation tools
- Performance monitoring integration
- Multi-instance deployment support
- Custom domain configuration
- SSL certificate automation
