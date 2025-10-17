# Configuration-Driven Deployment Guide

This document explains the new configuration-driven approach for deploying the LAMP stack to AWS Lightsail. Instead of hardcoding values in the workflow files, all configuration is now centralized in `deployment.config.yml`.

## Overview

The configuration-driven deployment system provides:

- **Centralized Configuration**: All deployment parameters in one YAML file
- **Environment Flexibility**: Easy switching between different environments
- **Maintainability**: No need to edit workflow files for configuration changes
- **Validation**: Configuration validation and error handling
- **Extensibility**: Easy to add new configuration options

## Files Structure

```
├── deployment.config.yml              # Main configuration file
├── .github/workflows/
│   ├── deploy-config-driven.yml       # New config-driven workflow
│   └── deploy-lamp-stack.yml          # Original workflow (for reference)
├── workflows/
│   ├── config_loader.py               # Configuration loader utility
│   ├── deploy-pre-steps-common.py     # Updated to use config
│   ├── deploy-post-steps-common.py    # Updated to use config
│   └── ... (other workflow scripts)
└── CONFIG_DRIVEN_DEPLOYMENT.md        # This documentation
```

## Configuration File Structure

### Main Sections

1. **AWS Configuration** - AWS region and credentials
2. **Lightsail Configuration** - Instance name, static IP
3. **Application Configuration** - PHP version, package files, environment variables
4. **Deployment Configuration** - Timeouts, retries, step configuration
5. **GitHub Actions Configuration** - Trigger and job settings
6. **Monitoring Configuration** - Health checks, performance monitoring
7. **Security Configuration** - File permissions, security settings
8. **Backup Configuration** - Backup settings and retention

### Example Configuration

```yaml
# AWS Configuration
aws:
  region: us-east-1

# Lightsail Instance Configuration
lightsail:
  instance_name: lamp-stack-demo
  static_ip: 98.91.3.69

# Application Configuration
application:
  name: lamp-stack-app
  version: "1.0.0"
  php_version: "8.1"
  package_files:
    - "index.php"
    - "css/"
    - "config/"
  environment_variables:
    APP_ENV: production
    APP_DEBUG: false
```

## How It Works

### 1. Configuration Loading

The workflow starts with a `load-config` job that:
- Reads `deployment.config.yml`
- Parses configuration values
- Determines deployment conditions based on branch and event type
- Sets GitHub Actions outputs for other jobs to use

### 2. Dynamic Job Execution

Jobs are conditionally executed based on configuration:
- Tests run only if `github_actions.jobs.test.enabled` is true
- Deployment steps can be individually enabled/disabled
- Branch-based deployment logic from configuration

### 3. Script Configuration

Python scripts use the `config_loader.py` utility to:
- Load configuration from multiple possible locations
- Provide typed access to configuration values
- Handle missing configuration with sensible defaults
- Validate configuration structure

## Usage Examples

### Basic Usage

1. **Update Configuration**: Edit `deployment.config.yml` with your values
2. **Commit Changes**: Push to trigger the workflow
3. **Monitor Deployment**: Check GitHub Actions for progress

### Advanced Configuration

#### Disable Specific Steps

```yaml
deployment:
  steps:
    pre_deployment:
      common:
        enabled: false  # Skip common pre-deployment steps
```

#### Custom Health Check

```yaml
monitoring:
  health_check:
    endpoint: "/health"
    expected_content: "OK"
    max_attempts: 15
    wait_between_attempts: 5
```

#### Environment-Specific Settings

```yaml
application:
  environment_variables:
    APP_ENV: staging
    DEBUG_MODE: true
    LOG_LEVEL: debug
```

### Command Line Overrides

Scripts support command-line overrides for configuration values:

```bash
# Override instance name and region
python3 workflows/deploy-pre-steps-common.py \
  --instance-name my-custom-instance \
  --region us-west-2

# Use custom configuration file
python3 workflows/deploy-post-steps-common.py \
  app.tar.gz \
  --config staging.config.yml
```

## Configuration Reference

### AWS Section

```yaml
aws:
  region: us-east-1  # AWS region for all resources
```

### Lightsail Section

```yaml
lightsail:
  instance_name: lamp-stack-demo  # Lightsail instance name
  static_ip: 98.91.3.69          # Static IP address
```

### Application Section

```yaml
application:
  name: lamp-stack-app           # Application name
  version: "1.0.0"              # Application version
  php_version: "8.1"            # PHP version for testing
  
  # Files to include in deployment package
  package_files:
    - "index.php"
    - "css/"
    - "config/"
  
  # Fallback to all files if specified files don't exist
  package_fallback: true
  
  # Environment variables to set on the instance
  environment_variables:
    APP_ENV: production
    APP_DEBUG: false
    APP_NAME: "LAMP Stack Demo"
```

### Deployment Section

```yaml
deployment:
  # Timeout settings (in seconds)
  timeouts:
    ssh_connection: 120
    command_execution: 300
    health_check: 180
  
  # Retry settings
  retries:
    max_attempts: 3
    ssh_connection: 5
  
  # Step configuration
  steps:
    pre_deployment:
      common:
        enabled: true
        update_packages: true
        create_directories: true
        backup_enabled: true
      lamp:
        enabled: true
        install_apache: true
        install_mysql: true
        install_php: true
        configure_firewall: true
```

### GitHub Actions Section

```yaml
github_actions:
  triggers:
    push_branches:
      - main
      - master
    pull_request_branches:
      - main
      - master
    workflow_dispatch: true
  
  jobs:
    test:
      enabled: true
      php_syntax_check: true
      local_server_test: true
    
    deployment:
      deploy_on_push: true
      deploy_on_pr: false
      artifact_retention_days: 1
```

### Monitoring Section

```yaml
monitoring:
  health_check:
    endpoint: "/"
    expected_content: "Hello Welcome"
    max_attempts: 10
    wait_between_attempts: 10
    initial_wait: 30
  
  performance:
    response_time_check: true
    http_headers_check: true
```

## Migration from Original Workflow

### Step 1: Update Configuration

1. Copy your current values from the original workflow to `deployment.config.yml`
2. Update instance name, static IP, and region as needed
3. Configure any custom settings (timeouts, retries, etc.)

### Step 2: Test Configuration

```bash
# Test configuration loading
python3 workflows/config_loader.py

# Test individual scripts
python3 workflows/deploy-pre-steps-common.py --help
```

### Step 3: Switch Workflows

1. Rename or disable the original workflow file
2. Ensure the new `deploy-config-driven.yml` workflow is active
3. Test with a small change to verify everything works

## Troubleshooting

### Configuration Errors

**Error**: `Configuration file not found`
- **Solution**: Ensure `deployment.config.yml` exists in the repository root

**Error**: `Invalid YAML in configuration file`
- **Solution**: Check YAML syntax, ensure proper indentation

**Error**: `KeyError: 'some_key'`
- **Solution**: Add missing configuration keys or check the configuration reference

### Deployment Issues

**Issue**: Jobs are skipped
- **Check**: `should_deploy` output in the `load-config` job
- **Solution**: Verify branch name and deployment settings in configuration

**Issue**: Scripts fail with configuration errors
- **Check**: Script logs for specific configuration issues
- **Solution**: Add missing configuration sections or use command-line overrides

### Performance Issues

**Issue**: Deployment takes too long
- **Solution**: Adjust timeout values in configuration:
  ```yaml
  deployment:
    timeouts:
      ssh_connection: 60      # Reduce from 120
      command_execution: 180  # Reduce from 300
  ```

**Issue**: Health checks fail
- **Solution**: Adjust health check parameters:
  ```yaml
  monitoring:
    health_check:
      max_attempts: 15        # Increase attempts
      wait_between_attempts: 15  # Increase wait time
  ```

## Best Practices

### Configuration Management

1. **Version Control**: Always commit configuration changes
2. **Environment Separation**: Use different config files for different environments
3. **Validation**: Test configuration changes in a development environment first
4. **Documentation**: Comment complex configuration sections

### Security

1. **Sensitive Data**: Never put secrets in configuration files
2. **File Permissions**: Use appropriate file permissions in security configuration
3. **Environment Variables**: Use GitHub Secrets for sensitive environment variables

### Maintenance

1. **Regular Updates**: Keep configuration up to date with infrastructure changes
2. **Monitoring**: Monitor deployment success rates and adjust timeouts as needed
3. **Cleanup**: Remove unused configuration options periodically

## Advanced Features

### Custom Configuration Files

You can use different configuration files for different environments:

```bash
# Development environment
python3 workflows/deploy-pre-steps-common.py --config dev.config.yml

# Staging environment
python3 workflows/deploy-pre-steps-common.py --config staging.config.yml
```

### Configuration Validation

The configuration loader includes validation:
- Required fields checking
- Type validation
- Default value handling
- Error reporting with helpful messages

### Extensibility

Adding new configuration options:

1. **Add to YAML**: Add new section to `deployment.config.yml`
2. **Update Loader**: Add getter method to `config_loader.py`
3. **Use in Scripts**: Access via configuration object in scripts
4. **Document**: Update this documentation

## Support

For issues or questions about the configuration-driven deployment:

1. Check this documentation first
2. Review the configuration file structure
3. Test with the configuration loader utility
4. Check GitHub Actions logs for specific error messages
5. Refer to the original workflow for comparison if needed

## Future Enhancements

Planned improvements:
- Configuration schema validation
- Multiple environment support
- Configuration templates
- Web-based configuration editor
- Integration with AWS Parameter Store
- Automated configuration backup and restore
