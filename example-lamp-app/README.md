# Example LAMP Stack Application

This is a sample PHP application demonstrating the generic deployment system.

## Features

- PHP 8.3 with Apache
- MySQL database integration
- Redis caching
- Responsive UI with CSS styling

## Files

- `index.php` - Main application file with database operations
- `config/database.php` - Database configuration
- `config/cache.php` - Redis cache configuration
- `css/style.css` - Application styling

## Deployment

This example app can be deployed using the parent repository's generic deployment system by configuring `deployment-generic.config.yml` with:

```yaml
dependencies:
  apache:
    enabled: true
  mysql:
    enabled: true
  php:
    enabled: true
    version: "8.3"
  redis:
    enabled: true
```

## Usage

1. Configure your deployment settings
2. Push to trigger GitHub Actions deployment
3. Access the application at your Lightsail instance IP
# Updated Sat Nov 15 01:31:38 PST 2025
# OIDC Test - Mon Nov 17 11:01:49 PST 2025
Sat Nov 22 15:42:50 PST 2025
Mon Nov 24 06:54:56 PST 2025
Mon Nov 24 06:58:23 PST 2025
