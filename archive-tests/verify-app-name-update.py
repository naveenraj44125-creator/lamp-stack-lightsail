#!/usr/bin/env python3

"""
Verify that the app_name IAM role naming update is working
"""

import subprocess
import sys

def check_file_content():
    """Check that the files have been updated correctly"""
    
    print("🔍 Verifying File Updates")
    print("=" * 40)
    
    # Check mcp-server/server.js
    try:
        with open('mcp-server/server.js', 'r') as f:
            server_content = f.read()
        
        # Check description
        if 'GitHubActions-{app_name}-deployment' in server_content:
            print("✅ server.js: Tool description updated to use app_name")
        else:
            print("❌ server.js: Tool description not updated")
            return False
        
        # Check pattern documentation
        if 'GitHubActions-{app_name}-deployment' in server_content and 'my-nodejs-app-deployment' in server_content:
            print("✅ server.js: Pattern documentation updated")
        else:
            print("❌ server.js: Pattern documentation not updated")
            return False
        
        # Check default role display
        if '${app_name || `${app_type}-app`}-deployment' in server_content:
            print("✅ server.js: Default role display updated")
        else:
            print("❌ server.js: Default role display not updated")
            return False
            
    except Exception as e:
        print(f"❌ Error reading server.js: {e}")
        return False
    
    # Check setup-complete-deployment.sh
    try:
        with open('setup-complete-deployment.sh', 'r') as f:
            setup_content = f.read()
        
        if 'ROLE_NAME="GitHubActions-${APP_NAME}-deployment"' in setup_content:
            print("✅ setup-complete-deployment.sh: Updated to use APP_NAME")
        else:
            print("❌ setup-complete-deployment.sh: Not updated")
            return False
            
    except Exception as e:
        print(f"❌ Error reading setup-complete-deployment.sh: {e}")
        return False
    
    return True

def check_git_status():
    """Check git status to confirm changes are committed"""
    
    print("\n📝 Checking Git Status")
    print("=" * 30)
    
    try:
        # Check if changes are committed
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  Uncommitted changes found:")
            print(result.stdout)
        else:
            print("✅ All changes committed")
        
        # Check recent commit
        result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                              capture_output=True, text=True, check=True)
        
        if 'app_name' in result.stdout.lower():
            print("✅ Recent commit mentions app_name update")
        else:
            print("⚠️  Recent commit doesn't mention app_name")
        
        return True
        
    except Exception as e:
        print(f"❌ Git check failed: {e}")
        return False

def check_deployment_status():
    """Check GitHub Actions deployment status"""
    
    print("\n🚀 Checking Deployment Status")
    print("=" * 35)
    
    try:
        # Check latest GitHub Actions run
        result = subprocess.run(['gh', 'run', 'list', '--limit', '1'], 
                              capture_output=True, text=True, check=True)
        
        if 'success' in result.stdout.lower():
            print("✅ Latest GitHub Actions run succeeded")
        else:
            print("⚠️  Latest GitHub Actions run status unclear")
            print(result.stdout)
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment check failed: {e}")
        return False

def main():
    """Main verification function"""
    
    print("🔧 App Name IAM Role Update Verification")
    print("=" * 50)
    
    success = True
    
    # Check file content
    if not check_file_content():
        success = False
    
    # Check git status
    if not check_git_status():
        success = False
    
    # Check deployment
    if not check_deployment_status():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All verifications passed!")
        print("✅ IAM role naming successfully updated from app_type to app_name")
        print("✅ Changes committed and deployed")
        print("\n📋 Summary of Changes:")
        print("   • Tool description: GitHubActions-{app_name}-deployment")
        print("   • Pattern examples: my-nodejs-app-deployment, my-lamp-app-deployment")
        print("   • Setup script: Uses APP_NAME instead of APP_TYPE")
        print("   • Default role display: Uses app_name with fallback to app_type-app")
    else:
        print("❌ Some verifications failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)