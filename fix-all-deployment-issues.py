#!/usr/bin/env python3
"""
Fix all deployment issues systematically
"""

import requests
import subprocess
import sys
import time
from typing import Dict, List, Tuple

class DeploymentFixer:
    def __init__(self):
        # Instance mapping from config files
        self.deployments = {
            "React Dashboard": {
                "instance": "react-dashboard-v6",
                "url": "http://35.171.85.222/",
                "expected": "react",
                "type": "nginx_static"
            },
            "Python Flask API": {
                "instance": "python-flask-api-v6", 
                "url": "http://18.232.114.213/",
                "expected": "Flask",
                "type": "nginx_proxy"
            },
            "Nginx Static Demo": {
                "instance": "nginx-static-demo-v6",
                "url": "http://18.215.255.226/",
                "expected": "Nginx",
                "type": "nginx_static"
            },
            "Node.js Application": {
                "instance": "simple-blog-1766109629",
                "url": "http://3.95.21.139:3000/",
                "expected": "Node.js",
                "type": "nodejs"
            },
            "LAMP Stack Demo": {
                "instance": "amazon-linux-test-v6",
                "url": None,  # Need to discover
                "expected": "Hello",
                "type": "lamp"
            },
            "Docker LAMP Demo": {
                "instance": "docker-lamp-demo-v6",
                "url": None,  # Need to discover
                "expected": "Docker",
                "type": "docker"
            },
            "Recipe Manager Docker": {
                "instance": "recipe-manager-docker-v6",
                "url": None,  # Need to discover
                "expected": "Recipe",
                "type": "docker"
            },
            "Social Media App": {
                "instance": "social-media-app-instance-1",
                "url": None,  # Need to discover
                "expected": "Social",
                "type": "nodejs_nginx"
            }
        }
    
    def test_endpoint(self, name: str, url: str, expected: str = None) -> Tuple[bool, str]:
        """Test an endpoint and return status"""
        print(f"🧪 Testing {name}: {url}")
        
        try:
            response = requests.get(url, timeout=15)
            content = response.text.lower()
            
            if response.status_code == 200:
                # Check for nginx default page
                nginx_indicators = [
                    "welcome to nginx",
                    "nginx.*default", 
                    "test page for the nginx"
                ]
                
                if any(indicator in content for indicator in nginx_indicators):
                    print("⚠️  NGINX DEFAULT PAGE DETECTED")
                    return False, "nginx_default"
                elif expected and expected.lower() in content:
                    print("✅ Working correctly")
                    return True, "success"
                else:
                    print(f"⚠️  Unexpected content (expected: {expected})")
                    return False, "wrong_content"
            else:
                print(f"❌ HTTP {response.status_code}")
                return False, f"http_{response.status_code}"
                
        except requests.exceptions.Timeout:
            print("❌ Connection timeout")
            return False, "timeout"
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed")
            return False, "connection_error"
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False, "error"
    
    def check_github_actions_status(self) -> Dict[str, str]:
        """Check GitHub Actions workflow status"""
        print("📊 Checking GitHub Actions status...")
        
        try:
            result = subprocess.run(
                ["gh", "run", "list", "--limit", "10", "--json", "name,status,conclusion"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                import json
                runs = json.loads(result.stdout)
                
                workflow_status = {}
                for run in runs:
                    name = run.get("name", "")
                    status = run.get("status", "")
                    conclusion = run.get("conclusion", "")
                    
                    if any(keyword in name.lower() for keyword in ["deploy", "lamp", "react", "python", "nginx", "node", "docker", "recipe", "social"]):
                        workflow_status[name] = conclusion or status
                
                return workflow_status
            else:
                print("⚠️  Could not check GitHub Actions status")
                return {}
                
        except Exception as e:
            print(f"⚠️  Error checking GitHub Actions: {str(e)}")
            return {}
    
    def trigger_missing_deployments(self, missing_deployments: List[str]) -> bool:
        """Trigger GitHub Actions for missing deployments"""
        if not missing_deployments:
            return True
        
        print(f"🚀 Triggering {len(missing_deployments)} missing deployments...")
        
        # Workflow name mapping
        workflow_mapping = {
            "LAMP Stack Demo": "Deploy LAMP Stack Example",
            "Docker LAMP Demo": "Deploy Basic Docker LAMP", 
            "Recipe Manager Docker": "Deploy Recipe Manager Docker App",
            "Social Media App": "Deploy Social Media App",
            "Node.js Application": "Node.js Application Deployment"
        }
        
        success_count = 0
        for deployment in missing_deployments:
            workflow_name = workflow_mapping.get(deployment)
            if workflow_name:
                try:
                    result = subprocess.run(
                        ["gh", "workflow", "run", workflow_name],
                        capture_output=True, text=True, timeout=30
                    )
                    
                    if result.returncode == 0:
                        print(f"✅ Triggered: {deployment}")
                        success_count += 1
                    else:
                        print(f"❌ Failed to trigger: {deployment}")
                        
                except Exception as e:
                    print(f"❌ Error triggering {deployment}: {str(e)}")
            else:
                print(f"⚠️  No workflow mapping for: {deployment}")
        
        return success_count > 0
    
    def fix_nginx_default_page(self, deployment_name: str) -> bool:
        """Fix nginx default page issue using troubleshooting tools"""
        print(f"🔧 Fixing nginx default page for {deployment_name}...")
        
        instance_name = self.deployments[deployment_name]["instance"]
        
        # Try using the nginx troubleshooting tool
        try:
            result = subprocess.run(
                ["python3", "troubleshooting-tools/nginx/fix-nginx.py", instance_name],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                print("✅ Nginx fix applied successfully")
                return True
            else:
                print(f"❌ Nginx fix failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error applying nginx fix: {str(e)}")
            return False
    
    def run_comprehensive_fix(self) -> bool:
        """Run comprehensive fix for all deployment issues"""
        print("🔧 COMPREHENSIVE DEPLOYMENT FIX")
        print("=" * 50)
        
        # Step 1: Test all known endpoints
        print("\n📋 Step 1: Testing All Known Endpoints")
        print("-" * 40)
        
        working = []
        nginx_issues = []
        connection_issues = []
        missing_deployments = []
        
        for name, config in self.deployments.items():
            if config["url"]:
                success, status = self.test_endpoint(name, config["url"], config["expected"])
                
                if success:
                    working.append(name)
                elif status == "nginx_default":
                    nginx_issues.append(name)
                elif status in ["timeout", "connection_error"]:
                    connection_issues.append(name)
            else:
                missing_deployments.append(name)
        
        print(f"\n📊 Current Status:")
        print(f"   ✅ Working: {len(working)}")
        print(f"   ⚠️  Nginx Issues: {len(nginx_issues)}")
        print(f"   ❌ Connection Issues: {len(connection_issues)}")
        print(f"   🚀 Missing/Unknown: {len(missing_deployments)}")
        
        # Step 2: Fix nginx default page issues
        if nginx_issues:
            print(f"\n🔧 Step 2: Fixing Nginx Default Page Issues")
            print("-" * 45)
            
            for deployment in nginx_issues:
                if self.fix_nginx_default_page(deployment):
                    # Re-test after fix
                    time.sleep(10)
                    config = self.deployments[deployment]
                    success, _ = self.test_endpoint(deployment, config["url"], config["expected"])
                    if success:
                        working.append(deployment)
                        nginx_issues.remove(deployment)
        
        # Step 3: Check GitHub Actions and trigger missing deployments
        print(f"\n🚀 Step 3: Checking and Triggering Missing Deployments")
        print("-" * 55)
        
        workflow_status = self.check_github_actions_status()
        
        if workflow_status:
            print("Recent workflow status:")
            for workflow, status in workflow_status.items():
                status_icon = "✅" if status == "success" else "❌" if status == "failure" else "🔄"
                print(f"   {status_icon} {workflow}: {status}")
        
        # Trigger missing deployments
        all_missing = missing_deployments + connection_issues
        if all_missing:
            if self.trigger_missing_deployments(all_missing):
                print("✅ Deployment workflows triggered")
                print("⏳ Wait 15-20 minutes for deployments to complete")
            else:
                print("❌ Failed to trigger some deployments")
        
        # Step 4: Final status report
        print(f"\n📊 Step 4: Final Status Report")
        print("-" * 35)
        
        total_deployments = len(self.deployments)
        working_count = len(working)
        
        print(f"Working deployments: {working_count}/{total_deployments}")
        
        if working:
            print("\n✅ Working deployments:")
            for deployment in working:
                url = self.deployments[deployment]["url"]
                print(f"   • {deployment}: {url}")
        
        if nginx_issues:
            print("\n⚠️  Still have nginx issues:")
            for deployment in nginx_issues:
                print(f"   • {deployment}")
        
        if connection_issues:
            print("\n❌ Still have connection issues:")
            for deployment in connection_issues:
                print(f"   • {deployment}")
        
        if missing_deployments:
            print("\n🚀 Deployments triggered (check in 15-20 minutes):")
            for deployment in missing_deployments:
                print(f"   • {deployment}")
        
        success_rate = working_count / total_deployments
        
        if success_rate >= 0.8:
            print(f"\n🎉 EXCELLENT: {success_rate:.0%} deployments working!")
        elif success_rate >= 0.6:
            print(f"\n👍 GOOD: {success_rate:.0%} deployments working")
        else:
            print(f"\n⚠️  NEEDS WORK: Only {success_rate:.0%} deployments working")
        
        return success_rate >= 0.6

def main():
    fixer = DeploymentFixer()
    
    print("🔧 DEPLOYMENT ISSUE FIXER")
    print("=" * 30)
    print("This script will:")
    print("1. Test all deployment endpoints")
    print("2. Fix nginx default page issues")
    print("3. Trigger missing deployments")
    print("4. Provide comprehensive status report")
    print("")
    
    success = fixer.run_comprehensive_fix()
    
    print(f"\n{'='*50}")
    if success:
        print("✅ DEPLOYMENT FIX COMPLETED SUCCESSFULLY")
        print("Most deployments are now working correctly.")
    else:
        print("⚠️  DEPLOYMENT FIX PARTIALLY COMPLETED")
        print("Some issues remain - check the report above.")
    
    print("\n💡 Next steps:")
    print("   • Wait 15-20 minutes for new deployments")
    print("   • Run: python3 verify-all-8-deployments.py")
    print("   • Use: ./monitor-all-deployments.sh for real-time monitoring")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())