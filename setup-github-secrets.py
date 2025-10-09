#!/usr/bin/env python3
"""
GitHub Secrets Setup Script for LAMP Stack Deployment
Helps configure the required secrets for GitHub Actions deployment
"""

import os
import sys

def print_header():
    """Print script header"""
    print("=" * 60)
    print("🔐 GitHub Secrets Setup for LAMP Stack Deployment")
    print("=" * 60)
    print()

def print_instructions():
    """Print setup instructions"""
    print("📋 Required GitHub Secrets:")
    print()
    
    print("1. AWS_ACCESS_KEY_ID")
    print("   - Your AWS access key ID")
    print("   - Used for AWS API authentication")
    print()
    
    print("2. AWS_SECRET_ACCESS_KEY")
    print("   - Your AWS secret access key")
    print("   - Used for AWS API authentication")
    print()
    
    print("3. LIGHTSAIL_SSH_PRIVATE_KEY")
    print("   - Content of the lamp-stack-demo-key.pem file")
    print("   - Used for SSH access to the Lightsail instance")
    print()
    
    print("🔧 How to add these secrets to GitHub:")
    print()
    print("1. Go to your GitHub repository")
    print("2. Click on 'Settings' tab")
    print("3. In the left sidebar, click 'Secrets and variables' > 'Actions'")
    print("4. Click 'New repository secret'")
    print("5. Add each secret with the exact name shown above")
    print()

def show_ssh_key_content():
    """Show SSH private key content if file exists"""
    key_file = "lamp-stack-demo-key.pem"
    
    if os.path.exists(key_file):
        print("🔑 SSH Private Key Content (for LIGHTSAIL_SSH_PRIVATE_KEY secret):")
        print("-" * 60)
        try:
            with open(key_file, 'r') as f:
                content = f.read()
                print(content)
        except Exception as e:
            print(f"❌ Error reading SSH key file: {e}")
        print("-" * 60)
        print()
        print("⚠️  Copy the entire content above (including BEGIN and END lines)")
        print("   and paste it as the value for LIGHTSAIL_SSH_PRIVATE_KEY secret")
        print()
    else:
        print(f"❌ SSH key file '{key_file}' not found in current directory")
        print("   Make sure you have the lamp-stack-demo-key.pem file")
        print()

def show_aws_credentials_info():
    """Show information about AWS credentials"""
    print("🔐 AWS Credentials Information:")
    print()
    print("You need AWS credentials with the following permissions:")
    print("- lightsail:GetInstance")
    print("- lightsail:GetInstances")
    print("- lightsail:GetStaticIp")
    print("- lightsail:GetStaticIps")
    print()
    print("To get your AWS credentials:")
    print("1. Go to AWS Console > IAM > Users")
    print("2. Select your user or create a new one")
    print("3. Go to 'Security credentials' tab")
    print("4. Click 'Create access key'")
    print("5. Choose 'Command Line Interface (CLI)'")
    print("6. Copy the Access Key ID and Secret Access Key")
    print()

def show_deployment_info():
    """Show deployment configuration information"""
    print("📋 Deployment Configuration:")
    print()
    print("Current configuration:")
    print("- Instance Name: lamp-stack-demo")
    print("- Static IP: 18.209.153.215")
    print("- Region: us-east-1")
    print("- SSH User: ubuntu")
    print()
    print("The GitHub Actions workflow will:")
    print("1. Test the PHP application")
    print("2. Deploy code to the pre-existing Lightsail instance")
    print("3. Verify the deployment is working")
    print()

def main():
    """Main function"""
    print_header()
    print_instructions()
    show_aws_credentials_info()
    show_ssh_key_content()
    show_deployment_info()
    
    print("✅ Setup Complete!")
    print()
    print("Next steps:")
    print("1. Add the three secrets to your GitHub repository")
    print("2. Push your code to the main branch")
    print("3. The GitHub Actions workflow will automatically deploy your application")
    print("4. Check the Actions tab in GitHub to monitor the deployment")
    print()
    print(f"🌐 Your application will be available at: http://18.209.153.215/")

if __name__ == "__main__":
    main()
