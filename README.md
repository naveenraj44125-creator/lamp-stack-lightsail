# LAMP Stack on AWS Lightsail

A simple LAMP (Linux, Apache, MySQL, PHP) stack application deployed to AWS Lightsail using GitHub Actions.

## 🌟 Features

- **Simple LAMP Stack**: Linux, Apache, MySQL, PHP
- **Responsive Design**: Modern CSS with gradients and animations
- **Database Integration**: MySQL database with sample data
- **Automated Deployment**: GitHub Actions CI/CD pipeline
- **Run Command Deployment**: Uses AWS Lightsail get-instance-access-details API
- **Health Monitoring**: Deployment verification and status checks

## 🏗️ Architecture

- **AWS Lightsail Instance**: Ubuntu 20.04 LTS
- **Static IP**: 44.194.47.34
- **Web Server**: Apache 2.4
- **Database**: MySQL 8.0
- **PHP**: Version 8.1
- **Deployment**: Run command API with GitHub Actions

## 🚀 Quick Start

### Prerequisites

1. AWS Account with Lightsail access
2. GitHub repository
3. Pre-created Lightsail instance (lamp-stack-demo)

### Infrastructure Setup

The infrastructure is manually pre-created and includes:
- Lightsail instance: `lamp-stack-demo`
- Static IP: `44.194.47.34`
- SSH key pair: `lamp-stack-demo-key.pem`
- Open ports: 80 (HTTP), 443 (HTTPS), 22 (SSH)

### GitHub Secrets Configuration

Configure the following GitHub secrets in your repository settings:

Required secrets:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

### Deployment

1. **Push to main branch**: GitHub Actions automatically deploys
2. **Manual deployment**: Use workflow_dispatch in GitHub Actions
3. **Local testing**: Run the deployment script locally

```bash
# Local deployment (for testing)
# First create the package
tar -czf app.tar.gz index.php css/ config/

# Then deploy using run command API
python3 deploy-with-run-command.py \
  lamp-stack-demo \
  app.tar.gz \
  --region us-east-1
```

## 📁 Project Structure

```
lamp_stack_lightsail/
├── index.php                         # Main application file
├── css/
│   └── style.css                     # Responsive CSS styles
├── config/
│   └── database.php                  # Database configuration
├── .github/
│   └── workflows/
│       └── deploy-lamp-stack.yml     # GitHub Actions workflow
├── deploy-with-run-command.py        # Application deployment script
├── install-lamp-on-lightsail-enhanced.py  # LAMP stack installation script
├── install-lamp-stack.sh             # Shell script for LAMP installation
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## 🔧 Application Features

### Web Application
- **Welcome Page**: Displays "Hello Welcome!" message
- **System Information**: Shows PHP version, server info, and deployment details
- **Database Test**: Connects to MySQL and displays sample data
- **Responsive Design**: Works on desktop and mobile devices

### Database Schema
```sql
CREATE DATABASE lamp_demo;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 GitHub Actions Workflow

The deployment pipeline includes:

1. **Test Phase**:
   - PHP syntax validation
   - Local application testing
   - Code quality checks

2. **Deploy Phase**:
   - SSH connection to Lightsail instance
   - LAMP stack installation (if needed)
   - Application file deployment
   - Service configuration and restart

3. **Verify Phase**:
   - Health checks for Apache and MySQL
   - Application response verification
   - Deployment status reporting

## 🔍 Monitoring & Verification

### Application URL
- **Production**: http://44.194.47.34/

### Health Checks
The deployment script automatically verifies:
- Apache service status
- MySQL service status
- Application file deployment
- Web server response
- Database connectivity

### Deployment Information
Each deployment includes metadata:
- GitHub commit SHA
- Branch name
- Deployment timestamp
- GitHub actor (who triggered deployment)

## 🛠️ Local Development

### Requirements
- PHP 8.1+
- MySQL 8.0+
- Apache 2.4+

### Setup
```bash
# Start local PHP server
php -S localhost:8000 index.php

# Access application
open http://localhost:8000
```

### Testing
```bash
# Validate PHP syntax
find . -name "*.php" -exec php -l {} \;

# Test application response
curl -f http://localhost:8000/
```

## 📋 Deployment Process

### Manual Infrastructure (One-time Setup)
1. Create Lightsail instance
2. Assign static IP
3. Configure security groups
4. Generate SSH key pair
5. Configure DNS (optional)

### Automated Code Deployment
1. Code changes pushed to main branch
2. GitHub Actions triggers workflow
3. Tests run automatically
4. Code deployed via SSH
5. Services restarted and verified
6. Deployment status reported

## 🔐 Security

- SSH key-based authentication
- Secure GitHub secrets management
- Minimal required AWS permissions
- Regular security updates via deployment

## 🐛 Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   - Verify SSH key is correct
   - Check instance is running
   - Confirm security group allows SSH (port 22)

2. **Application Not Loading**
   - Check Apache service status
   - Verify file permissions
   - Review Apache error logs

3. **Database Connection Failed**
   - Confirm MySQL service is running
   - Check database credentials
   - Verify database exists

### Debug Commands
```bash
# Check service status
sudo systemctl status apache2
sudo systemctl status mysql

# View logs
sudo tail -f /var/log/apache2/error.log
sudo tail -f /var/log/mysql/error.log

# Test application
curl -v http://localhost/
```

## 📚 Additional Resources

- [AWS Lightsail Documentation](https://docs.aws.amazon.com/lightsail/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PHP Documentation](https://www.php.net/docs.php)
- [Apache Documentation](https://httpd.apache.org/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
# Trigger workflow - Thu Oct  9 08:20:40 PDT 2025
# Modular LAMP Stack Deployment - Fri Oct 10 10:41:33 PDT 2025
# Trigger deployment - Thu Oct 16 07:58:42 PDT 2025
