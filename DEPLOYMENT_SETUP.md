# LAMP Stack Lightsail Deployment Setup

## Project Overview

This project contains a complete LAMP stack application with automated deployment to AWS Lightsail using GitHub Actions and Terraform. The deployment uses `run_commands` instead of `user_data` for better control and reliability.

## Project Structure

```
lamp_stack_lightsail/
├── README.md                           # Complete project documentation
├── requirements.txt                    # Python dependencies
├── deploy-with-run-command.py         # Main deployment script (executable)
├── index.php                          # Main application file
├── .github/
│   └── workflows/
│       └── deploy-to-lightsail.yml    # GitHub Actions workflow
├── config/
│   └── database.php                   # Database configuration
├── css/
│   └── style.css                      # Application styling
└── terraform/
    ├── main.tf                        # Main Terraform configuration
    ├── variables.tf                   # Terraform variables
    └── outputs.tf                     # Terraform outputs
```

## Key Features

### Application Features
- **LAMP Stack**: Linux + Apache + MySQL + PHP
- **Responsive Design**: Mobile-friendly interface with CSS animations
- **Database Integration**: PDO-based MySQL connectivity with error handling
- **System Information**: Displays PHP version, server info, and database status
- **Modern UI**: Gradient backgrounds, animations, and clean design

### Infrastructure Features
- **AWS Lightsail**: Nano instance (cost-effective)
- **Static IP**: Consistent public IP address
- **Security**: Proper port configuration (22, 80, 443)
- **Key Pair**: SSH access for troubleshooting

### Deployment Features
- **GitHub Actions**: Automated CI/CD pipeline
- **Terraform**: Infrastructure as Code
- **Run Commands**: Reliable deployment using AWS Lightsail API
- **Multi-stage**: Test → Infrastructure → Application deployment
- **Error Handling**: Comprehensive error checking and reporting

## Deployment Method

This project uses **run_commands** deployment method instead of user_data:

### Advantages of run_commands:
1. **Better Control**: Execute commands after instance is fully running
2. **Error Handling**: Real-time feedback on command execution
3. **Debugging**: Easier to troubleshoot deployment issues
4. **Flexibility**: Can run multiple deployment phases
5. **Reliability**: Commands execute in sequence with status monitoring

### Deployment Process:
1. **Infrastructure**: Terraform creates Lightsail instance, static IP, and key pair
2. **Wait for Ready**: Script waits for instance to be in running state
3. **LAMP Installation**: Installs Apache, MySQL, PHP, and dependencies
4. **Configuration**: Configures services and database
5. **Application Deployment**: Deploys PHP application files
6. **Verification**: Tests deployment and displays access information

## Required GitHub Secrets

To use this project, you'll need to configure these GitHub repository secrets:

```
AWS_ACCESS_KEY_ID          # AWS access key for Lightsail
AWS_SECRET_ACCESS_KEY      # AWS secret key for Lightsail
AWS_REGION                 # AWS region (default: us-east-1)
INSTANCE_NAME              # Lightsail instance name (default: lamp-stack-demo)
```

## Next Steps

### 1. Create GitHub Repository
```bash
# Navigate to the lamp_stack_lightsail directory
cd lamp_stack_lightsail

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial LAMP stack application with Lightsail deployment"

# Create GitHub repository (replace with your username)
gh repo create lamp-stack-lightsail --public --source=. --remote=origin --push
```

### 2. Configure GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the required secrets listed above.

### 3. Configure AWS Credentials
Ensure your AWS credentials have the following permissions:
- `lightsail:*` (or specific Lightsail permissions)
- `ec2:DescribeKeyPairs` (for key pair operations)

### 4. Deploy
Push changes to the main branch to trigger the deployment:
```bash
git push origin main
```

## Monitoring Deployment

1. **GitHub Actions**: Monitor the workflow in the Actions tab
2. **Terraform**: Check infrastructure creation logs
3. **Deployment Script**: Monitor application deployment progress
4. **Access Application**: Use the provided IP address from deployment output

## Troubleshooting

### Common Issues:
1. **AWS Credentials**: Ensure secrets are correctly configured
2. **Instance State**: Deployment waits for instance to be running
3. **Command Timeout**: Large packages may take time to install
4. **Database Connection**: Check MySQL service status and credentials

### Debug Commands:
```bash
# Check instance status
aws lightsail get-instance --instance-name lamp-stack-demo

# Check recent operations
aws lightsail get-operations

# SSH into instance (if needed)
ssh -i ~/.ssh/lamp-stack-key ubuntu@<instance-ip>
```

## Application Access

After successful deployment:
- **URL**: `http://<static-ip-address>`
- **Features**: Welcome message, system info, database status
- **Mobile**: Responsive design works on all devices

## Cost Estimation

- **Lightsail Nano**: ~$3.50/month
- **Static IP**: Free (when attached)
- **Data Transfer**: 1TB included
- **Total**: ~$3.50/month

## Security Notes

- Default MySQL passwords are set in the deployment script
- Change default passwords for production use
- Consider enabling HTTPS with Let's Encrypt
- Regular security updates recommended

## Support

For issues or questions:
1. Check GitHub Actions logs
2. Review Terraform outputs
3. Check AWS Lightsail console
4. Review deployment script logs

---

**Ready to deploy!** Follow the next steps to create your GitHub repository and start the automated deployment process.
