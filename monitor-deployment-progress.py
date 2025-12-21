#!/usr/bin/env python3
"""
Monitor deployment progress and verify endpoints when ready
"""

import subprocess
import time
import sys
import json

def check_workflow_status():
    """Check GitHub Actions workflow status"""
    try:
        result = subprocess.run(
            ["gh", "run", "list", "--limit", "10", "--json", "name,status,conclusion,createdAt"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            runs = json.loads(result.stdout)
            
            # Filter for recent deployment workflows
            deployment_runs = []
            for run in runs:
                name = run.get("name", "")
                if any(keyword in name.lower() for keyword in ["deploy", "lamp", "react", "python", "nginx", "node", "docker", "recipe", "social"]):
                    deployment_runs.append({
                        "name": name,
                        "status": run.get("status", ""),
                        "conclusion": run.get("conclusion", ""),
                        "created": run.get("createdAt", "")
                    })
            
            return deployment_runs[:8]  # Top 8 most recent
        else:
            return []
            
    except Exception as e:
        print(f"Error checking workflows: {str(e)}")
        return []

def display_status(runs):
    """Display workflow status"""
    print(f"\n📊 Deployment Status ({time.strftime('%H:%M:%S')})")
    print("-" * 50)
    
    running_count = 0
    success_count = 0
    failed_count = 0
    
    for run in runs:
        name = run["name"]
        status = run["status"]
        conclusion = run["conclusion"]
        
        if status == "in_progress":
            icon = "🔄"
            status_text = "RUNNING"
            running_count += 1
        elif conclusion == "success":
            icon = "✅"
            status_text = "SUCCESS"
            success_count += 1
        elif conclusion == "failure":
            icon = "❌"
            status_text = "FAILED"
            failed_count += 1
        else:
            icon = "⏳"
            status_text = status.upper()
        
        print(f"{icon} {name:<35} {status_text}")
    
    print(f"\nSummary: ✅{success_count} 🔄{running_count} ❌{failed_count}")
    
    return running_count, success_count, failed_count

def verify_endpoints():
    """Run endpoint verification"""
    print("\n🔍 Running endpoint verification...")
    try:
        result = subprocess.run(
            ["python3", "verify-all-8-deployments.py"],
            capture_output=True, text=True, timeout=120
        )
        
        # Show just the summary part
        output_lines = result.stdout.split('\n')
        summary_started = False
        
        for line in output_lines:
            if "DEPLOYMENT STATUS SUMMARY" in line:
                summary_started = True
            if summary_started:
                print(line)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running verification: {str(e)}")
        return False

def main():
    print("🚀 Monitoring Deployment Progress")
    print("=" * 40)
    print("Monitoring GitHub Actions workflows...")
    print("Press Ctrl+C to stop monitoring")
    
    check_count = 0
    max_checks = 30  # Monitor for up to 15 minutes (30 * 30 seconds)
    
    try:
        while check_count < max_checks:
            runs = check_workflow_status()
            
            if runs:
                running_count, success_count, failed_count = display_status(runs)
                
                # If no workflows are running, verify endpoints
                if running_count == 0:
                    print("\n🎉 All workflows completed!")
                    
                    if success_count >= 6:  # Most deployments successful
                        print("✅ Most deployments successful - verifying endpoints...")
                        verify_endpoints()
                        break
                    else:
                        print("⚠️  Some deployments failed - checking endpoints anyway...")
                        verify_endpoints()
                        break
                
                # If still running, wait and check again
                if running_count > 0:
                    print(f"\n⏳ {running_count} workflows still running... (check {check_count + 1}/{max_checks})")
                    time.sleep(30)  # Wait 30 seconds
                    check_count += 1
            else:
                print("❌ Could not get workflow status")
                break
        
        if check_count >= max_checks:
            print("\n⏰ Monitoring timeout reached")
            print("Some deployments may still be running")
            print("Run 'gh run list' to check current status")
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")
        print("Run 'python3 verify-all-8-deployments.py' to check endpoints manually")
    
    print("\n💡 Next steps:")
    print("   • Run: python3 verify-all-8-deployments.py")
    print("   • Use: ./monitor-all-deployments.sh for ongoing monitoring")
    print("   • Check: gh run list for workflow status")

if __name__ == '__main__':
    main()