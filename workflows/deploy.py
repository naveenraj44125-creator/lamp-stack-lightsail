#!/usr/bin/env python3
"""
Complete Deployment Script for AWS Lightsail
This script orchestrates the entire deployment process
"""

import sys
import os
import argparse
import subprocess
import time
from datetime import datetime
from config_loader import DeploymentConfig

def run_script(script_path, args_list=None, description=""):
    """Run a Python script with arguments"""
    if args_list is None:
        args_list = []
    
    cmd = ['python3', script_path] + args_list
    print(f"\n🚀 {description}")
    print(f"📝 Command: {' '.join(cmd)}")
    print("-" * 60)
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=False, text=True)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"\n⏱️  Duration: {duration:.2f} seconds")
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully")
        return True
    else:
        print(f"❌ {description} failed with exit code {result.returncode}")
        return False

def create_package(package_files, package_name="app-package.tar.gz"):
    """Create deployment package"""
    print(f"\n📦 Creating deployment package: {package_name}")
    
    # Check if files exist
    missing_files = []
    for file_path in package_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    # Create tar.gz package
    cmd = ['tar', '-czf', package_name] + package_files
    print(f"📝 Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Get package size
        size = os.path.getsize(package_name)
        size_mb = size / (1024 * 1024)
        print(f"✅ Package created successfully")
        print(f"📊 Package size: {size_mb:.2f} MB")
        print(f"📁 Files included: {len(package_files)}")
        return True
    else:
        print(f"❌ Failed to create package: {result.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Complete deployment script for AWS Lightsail')
    parser.add_argument('--instance-name', help='Lightsail instance name')
    parser.add_argument('--region', help='AWS region')
    parser.add_argument('--config-file', help='Path to configuration file')
    parser.add_argument('--skip-pre', action='store_true', help='Skip pre-deployment steps')
    parser.add_argument('--skip-post', action='store_true', help='Skip post-deployment steps')
    parser.add_argument('--verify', action='store_true', help='Verify deployment')
    parser.add_argument('--cleanup', action='store_true', help='Clean up temporary files')
    parser.add_argument('--monitor', action='store_true', help='Run health check after deployment')
    parser.add_argument('--package-name', default='app-package.tar.gz', help='Name of deployment package')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config_file = args.config_file if args.config_file else 'deployment-generic.config.yml'
        
        print("="*80)
        print("🚀 AWS LIGHTSAIL DEPLOYMENT ORCHESTRATOR")
        print("="*80)
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📋 Config: {config_file}")
        
        # Check if config file exists
        if not os.path.exists(config_file):
            print(f"❌ Configuration file not found: {config_file}")
            print("💡 Please create a configuration file or specify --config-file")
            sys.exit(1)
        
        config = DeploymentConfig(config_file=config_file)
        
        # Get configuration values
        instance_name = args.instance_name or config.get_instance_name()
        region = args.region or config.get_aws_region()
        package_files = config.get_package_files()
        
        print(f"🌍 Instance: {instance_name}")
        print(f"📍 Region: {region}")
        print(f"📦 Package: {args.package_name}")
        
        # Build script arguments
        script_args = []
        if args.instance_name:
            script_args.extend(['--instance-name', args.instance_name])
        if args.region:
            script_args.extend(['--region', args.region])
        if args.config_file:
            script_args.extend(['--config-file', args.config_file])
        
        deployment_success = True
        
        # Step 1: Pre-deployment (install dependencies)
        if not args.skip_pre:
            if not run_script(
                'workflows/deploy-pre-steps-generic.py',
                script_args,
                "STEP 1: PRE-DEPLOYMENT (Installing Dependencies)"
            ):
                deployment_success = False
        else:
            print("\n⏭️  Skipping pre-deployment steps")
        
        # Step 2: Create deployment package
        if deployment_success:
            print(f"\n" + "="*80)
            print("📦 STEP 2: CREATING DEPLOYMENT PACKAGE")
            print("="*80)
            
            if not create_package(package_files, args.package_name):
                deployment_success = False
        
        # Step 3: Post-deployment (deploy application)
        if deployment_success and not args.skip_post:
            post_args = script_args + [args.package_name]
            if args.verify:
                post_args.append('--verify')
            if args.cleanup:
                post_args.append('--cleanup')
            
            if not run_script(
                'workflows/deploy-post-steps-generic.py',
                post_args,
                "STEP 3: POST-DEPLOYMENT (Deploying Application)"
            ):
                deployment_success = False
        elif args.skip_post:
            print("\n⏭️  Skipping post-deployment steps")
        
        # Step 4: Health check (optional)
        if deployment_success and args.monitor:
            monitor_args = script_args + ['health']
            run_script(
                'workflows/deployment_monitor.py',
                monitor_args,
                "STEP 4: HEALTH CHECK (Monitoring Deployment)"
            )
        
        # Final summary
        print(f"\n" + "="*80)
        if deployment_success:
            print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("="*80)
            print(f"✅ Instance: {instance_name}")
            print(f"✅ Region: {region}")
            print(f"✅ Package: {args.package_name}")
            
            # Get instance info for final summary
            try:
                from lightsail_common import LightsailBase
                client = LightsailBase(instance_name, region)
                instance_info = client.get_instance_info()
                if instance_info and instance_info.get('public_ip'):
                    print(f"🌐 URL: http://{instance_info['public_ip']}")
            except:
                pass
            
            print(f"\n💡 Next Steps:")
            print(f"   🔍 Monitor: python3 workflows/deployment_monitor.py health")
            print(f"   📋 Logs: python3 workflows/deployment_monitor.py logs")
            print(f"   🔄 Restart: python3 workflows/deployment_monitor.py restart")
            
        else:
            print("❌ DEPLOYMENT FAILED!")
            print("="*80)
            print("💡 Troubleshooting:")
            print("   🔍 Check logs above for error details")
            print("   🔄 Try running individual steps manually")
            print("   📋 Verify configuration file settings")
            print("   🌐 Check AWS credentials and permissions")
        
        print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        sys.exit(0 if deployment_success else 1)
        
    except Exception as e:
        print(f"❌ Deployment orchestrator error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()