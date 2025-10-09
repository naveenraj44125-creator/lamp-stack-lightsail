#!/usr/bin/env python3
"""
GitHub Repository Secrets Configuration Script
Configures AWS credentials as GitHub repository secrets for LAMP Stack deployment
"""

import json
import os
import sys
import subprocess

def check_github_cli():
    """Check if GitHub CLI is installed and authenticated"""
    try:
        result = subprocess.run(['gh', 'auth', 'status'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ GitHub CLI is authenticated")
            return True
        else:
            print("❌ GitHub CLI not authenticated")
            print("Please run: gh auth login")
            return False
    except FileNotFoundError:
        print("❌ GitHub CLI not installed")
        print("Please install GitHub CLI: https://cli.github.com/")
        return False

def load_aws_credentials():
    """Load AWS credentials from the generated file"""
    try:
        with open('aws-credentials.json', 'r') as f:
            credentials = json.load(f)
        print("✅ Loaded AWS credentials from aws-credentials.json")
        return credentials
    except FileNotFoundError:
        print("❌ aws-credentials.json not found")
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON in aws-credentials.json")
        return None

def set_github_secret(repo, secret_name, secret_value):
    """Set a GitHub repository secret using GitHub CLI"""
    try:
        cmd = ['gh', 'secret', 'set', secret_name, 
               '--repo', repo, '--body', secret_value]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Set secret: {secret_name}")
            return True
        else:
            print(f"❌ Failed to set secret {secret_name}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting secret {secret_name}: {str(e)}")
        return False

def configure_repository_secrets():
    """Configure all required GitHub repository secrets"""
    repo = "naveenraj44125-creator/lamp-stack-lightsail"
    
    print(f"🔐 Configuring GitHub secrets for repository: {repo}")
    print("-" * 60)
    
    # Check GitHub CLI
    if not check_github_cli():
        return False
    
    # Load AWS credentials
    credentials = load_aws_credentials()
    if not credentials:
        return False
    
    # Set each secret
    secrets_to_set = [
        ('AWS_ACCESS_KEY_ID', credentials['AWS_ACCESS_KEY_ID']),
        ('AWS_SECRET_ACCESS_KEY', credentials['AWS_SECRET_ACCESS_KEY']),
        ('AWS_REGION', credentials['AWS_REGION'])
    ]
    
    success_count = 0
    for secret_name, secret_value in secrets_to_set:
        if set_github_secret(repo, secret_name, secret_value):
            success_count += 1
    
    if success_count == len(secrets_to_set):
        print(f"\n🎉 Successfully configured all {success_count} GitHub secrets!")
        return True
    else:
        print(f"\n⚠️  Configured {success_count}/{len(secrets_to_set)} secrets")
        return False

def list_current_secrets():
    """List current repository secrets"""
    repo = "naveenraj44125-creator/lamp-stack-lightsail"
    
    try:
        cmd = ['gh', 'secret', 'list', '--repo', repo]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n📋 Current secrets in {repo}:")
            print(result.stdout)
        else:
            print(f"❌ Could not list secrets: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error listing secrets: {str(e)}")

def main():
    print("🔐 GitHub Repository Secrets Configuration")
    print("=" * 50)
    
    # Load and display credentials
    credentials = load_aws_credentials()
    if credentials:
        print("\n📋 AWS Credentials to be configured:")
        print(f"   AWS_ACCESS_KEY_ID: {credentials['AWS_ACCESS_KEY_ID']}")
        print(f"   AWS_SECRET_ACCESS_KEY: {credentials['AWS_SECRET_ACCESS_KEY'][:8]}...")
        print(f"   AWS_REGION: {credentials['AWS_REGION']}")
    
    # List current secrets first
    list_current_secrets()
    
    # Configure secrets
    success = configure_repository_secrets()
    
    if success:
        print("\n✅ GitHub secrets configuration completed!")
        print("\nNext steps:")
        print("1. Push code to trigger GitHub Actions")
        print("2. Monitor deployment: https://github.com/naveenraj44125-creator/lamp-stack-lightsail/actions")
        print("3. Check Lightsail instance after deployment")
    else:
        print("\n❌ GitHub secrets configuration failed")
        print("\nManual setup instructions:")
        print("1. Go to: https://github.com/naveenraj44125-creator/lamp-stack-lightsail/settings/secrets/actions")
        print("2. Click 'New repository secret'")
        print("3. Add the following secrets:")
        if credentials:
            print(f"   - Name: AWS_ACCESS_KEY_ID, Value: {credentials['AWS_ACCESS_KEY_ID']}")
            print(f"   - Name: AWS_SECRET_ACCESS_KEY, Value: {credentials['AWS_SECRET_ACCESS_KEY']}")
            print(f"   - Name: AWS_REGION, Value: {credentials['AWS_REGION']}")

if __name__ == '__main__':
    main()
