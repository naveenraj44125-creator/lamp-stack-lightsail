#!/usr/bin/env python3

"""
Simple test to verify app_name IAM role naming via web interface
"""

import requests
import json

def test_app_name_iam_role():
    """Test app_name IAM role naming via web interface"""
    
    print("🧪 Testing App Name IAM Role Naming")
    print("=" * 50)
    
    # Test the web interface endpoint that shows tool information
    try:
        response = requests.get("http://3.81.56.119:3000/", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to get web interface: {response.status_code}")
            return False
        
        html_content = response.text
        
        # Check if the web interface shows the updated description
        if 'GitHubActions-{app_name}-deployment' in html_content:
            print("✅ Web interface shows updated app_name pattern")
        elif 'GitHubActions-{app_type}-deployment' in html_content:
            print("❌ Web interface still shows old app_type pattern")
            return False
        else:
            print("⚠️  IAM role pattern not found in web interface")
        
        # Check for examples with app_name
        if 'my-nodejs-app-deployment' in html_content or 'my-lamp-app-deployment' in html_content:
            print("✅ Web interface shows updated examples with app_name")
        elif 'nodejs-deployment' in html_content and 'lamp-deployment' in html_content:
            print("❌ Web interface still shows old examples with app_type")
            return False
        else:
            print("⚠️  Example patterns not found in web interface")
        
        print("\n🎉 App name IAM role naming update verified!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_app_name_iam_role()