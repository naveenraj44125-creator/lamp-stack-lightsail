# AWS Lightsail RDS Integration Guide

## Overview

This guide explains how to use the new AWS Lightsail RDS (Relational Database Service) integration feature with the Generic Deployment System. Instead of installing a local database on your Lightsail instance, you can now connect to an external RDS database with dynamic credential retrieval.

## Key Features

- **Dynamic Credential Retrieval**: Automatically fetches RDS passwords using AWS Lightsail API instead of hardcoded credentials
- **Multi-Database Support**: Works with both MySQL and PostgreSQL RDS instances
- **Environment Variable Management**: Automatically configures database connection details as environment variables
- **Seamless Integration**: Works with existing application code without modifications
- **Security**: Credentials are retrieved securely from AWS and stored in protected environment files

## Prerequisites

1. **AWS Lightsail RDS Instance**: You must have a Lightsail RDS database already created
2. **AWS Credentials**: GitHub Secrets configured with AWS access credentials
3. **Network Access**: Your Lightsail instance must have network access to the RDS instance

## Configuration

### 1. GitHub Secrets Setup

Add these secrets to your GitHub repository:

```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

### 2. Configuration File Setup

Use the RDS configuration in your deployment config file:

```yaml
# Example: deployment-rds-example.config.yml
dependencies:
  # External MySQL RDS Database Configuration
  mysql:
    enabled: true
    external: true  # This enables RDS integration
    rds:
      # RDS Database Configuration
      database_name: "my-rds-database"  # Name of your Lightsail RDS instance
      region: "us-east-1"               # AWS region where RDS is located
      
      # AWS Credentials for RDS API access (GitHub Secrets)
      access_key: "${AWS_ACCESS_KEY_ID}"
      secret_key: "${AWS_SECRET_ACCESS_KEY}"
      
      # Optional: Custom environment variables
      environment:
        DB_CONNECTION_TIMEOUT: "30"
        DB_CHARSET: "utf8mb4"
        DB_COLLATION: "utf8mb4_unicode_ci"

  # Alternative: PostgreSQL RDS Configuration
  postgresql:
    enabled: false
    external: true
    rds:
      database_name: "my-postgres-rds"
      region: "us-east-1"
      access_key: "${AWS_ACCESS_KEY_ID}"
      secret_key: "${AWS_SECRET_ACCESS_KEY}"
      environment:
        DB_CONNECTION_TIMEOUT: "30"
        DB_SSLMODE: "require"
```

## How It Works

### 1. Deployment Process

When you deploy with RDS configuration:

1. **RDS Manager Initialization**: The system initializes the Lightsail RDS manager with your AWS credentials
2. **Connection Details Retrieval**: Automatically fetches RDS connection details including:
   - Host endpoint
   - Port number
   - Database name
   - Username
   - **Password** (retrieved dynamically from AWS)
3. **Client Installation**: Installs the appropriate database client (mysql-client or postgresql-client)
4. **Environment Configuration**: Creates environment variables for your application
5. **Connectivity Testing**: Tests the database connection from the Lightsail instance

### 2. Environment Variables Created

The system automatically creates these environment variables:

```bash
DB_TYPE=MYSQL                    # or POSTGRESQL
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=3306                     # or 5432 for PostgreSQL
DB_NAME=your_database_name
DB_USERNAME=your_db_username
DB_PASSWORD=dynamically_retrieved_password
DB_EXTERNAL=true
```

### 3. Application Integration

Your PHP application automatically detects RDS configuration:

```php
// config/database.php automatically handles RDS
if ($isExternalDB) {
    // Uses environment variables from RDS
    define('DB_HOST', $_ENV['DB_HOST']);
    define('DB_NAME', $_ENV['DB_NAME']);
    // ... etc
} else {
    // Falls back to local database
    define('DB_HOST', 'localhost');
    // ... etc
}
```

## Usage Examples

### Example 1: MySQL RDS

```yaml
dependencies:
  mysql:
    enabled: true
    external: true
    rds:
      database_name: "production-mysql-db"
      region: "us-east-1"
      access_key: "${AWS_ACCESS_KEY_ID}"
      secret_key: "${AWS_SECRET_ACCESS_KEY}"
```

### Example 2: PostgreSQL RDS

```yaml
dependencies:
  postgresql:
    enabled: true
    external: true
    rds:
      database_name: "production-postgres-db"
      region: "us-west-2"
      access_key: "${AWS_ACCESS_KEY_ID}"
      secret_key: "${AWS_SECRET_ACCESS_KEY}"
      environment:
        DB_SSLMODE: "require"
```

## Security Considerations

1. **AWS Credentials**: Store AWS credentials as GitHub Secrets, never in code
2. **Environment Files**: Database credentials are stored in `/opt/app/database.env` with restricted permissions (600)
3. **Network Security**: Ensure your RDS security groups allow connections from your Lightsail instance
4. **Password Rotation**: The system retrieves passwords dynamically, supporting AWS password rotation

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check RDS security groups and network connectivity
2. **Authentication Failed**: Verify AWS credentials and RDS instance name
3. **Database Not Found**: Ensure the RDS instance name matches configuration

### Debug Information

The deployment process provides detailed logging:

```
🔗 Configuring external MYSQL RDS database...
📡 Retrieving RDS connection details for my-rds-database...
📦 Installing mysql client...
🔍 Testing database connectivity...
⚙️  Configuring environment variables...
✅ External MYSQL RDS database configured successfully
   Host: my-rds.region.rds.amazonaws.com
   Port: 3306
   Database: myapp
   Username: admin
```

## File Structure

The RDS integration includes these key files:

```
workflows/
├── lightsail_rds.py          # RDS management and API integration
├── dependency_manager.py     # Updated with RDS support
└── config_loader.py          # Configuration parsing

config/
└── database.php              # Updated with RDS environment variable support

deployment-rds-example.config.yml  # Example RDS configuration
```

## Migration from Local Database

To migrate from local database to RDS:

1. **Create RDS Instance**: Set up your Lightsail RDS database
2. **Update Configuration**: Change `external: false` to `external: true` and add RDS configuration
3. **Add GitHub Secrets**: Configure AWS credentials
4. **Deploy**: The system will automatically use RDS instead of local database

## Benefits

- **Managed Database**: AWS handles backups, updates, and maintenance
- **Scalability**: Easy to scale database resources independently
- **High Availability**: RDS provides built-in redundancy and failover
- **Security**: Dynamic credential retrieval eliminates hardcoded passwords
- **Monitoring**: AWS provides comprehensive database monitoring

## Next Steps

1. Create your Lightsail RDS instance in the AWS console
2. Configure your deployment config file with RDS settings
3. Add AWS credentials to GitHub Secrets
4. Deploy your application with RDS integration

For more information, see the example configuration in `deployment-rds-example.config.yml`.
