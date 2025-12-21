#!/usr/bin/env python3
"""
Extract instance names and deployment info from config files
"""

import yaml
import glob
import sys

def extract_deployment_info():
    """Extract deployment information from all config files"""
    
    deployments = []
    
    # Find all deployment config files
    config_files = glob.glob("deployment-*.config.yml")
    
    for config_file in sorted(config_files):
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Extract key information
            deployment_info = {
                "config_file": config_file,
                "app_name": config_file.replace("deployment-", "").replace(".config.yml", ""),
                "instance_name": config.get("lightsail", {}).get("instance_name", "N/A"),
                "app_type": config.get("application", {}).get("type", "N/A"),
                "blueprint": config.get("lightsail", {}).get("blueprint_id", "ubuntu_22_04"),
                "bundle": config.get("lightsail", {}).get("bundle_id", "nano_3_0"),
                "nginx_enabled": config.get("dependencies", {}).get("nginx", {}).get("enabled", False),
                "nodejs_enabled": config.get("dependencies", {}).get("nodejs", {}).get("enabled", False),
                "python_enabled": config.get("dependencies", {}).get("python", {}).get("enabled", False),
                "docker_enabled": config.get("dependencies", {}).get("docker", {}).get("enabled", False),
                "use_docker": config.get("deployment", {}).get("use_docker", False),
                "health_endpoint": config.get("monitoring", {}).get("health_check", {}).get("endpoint", "/"),
                "expected_content": config.get("monitoring", {}).get("health_check", {}).get("expected_content", "")
            }
            
            deployments.append(deployment_info)
            
        except Exception as e:
            print(f"❌ Error reading {config_file}: {str(e)}")
    
    return deployments

def main():
    print("🔍 Extracting Deployment Information from Config Files")
    print("=" * 60)
    
    deployments = extract_deployment_info()
    
    if not deployments:
        print("❌ No deployment config files found!")
        return 1
    
    print(f"📋 Found {len(deployments)} deployment configurations:\n")
    
    # Display summary table
    print(f"{'App Name':<20} {'Instance Name':<25} {'Type':<10} {'Tech Stack':<15}")
    print("-" * 75)
    
    for dep in deployments:
        # Determine tech stack
        tech_stack = []
        if dep["use_docker"]:
            tech_stack.append("Docker")
        if dep["nginx_enabled"]:
            tech_stack.append("Nginx")
        if dep["nodejs_enabled"]:
            tech_stack.append("Node.js")
        if dep["python_enabled"]:
            tech_stack.append("Python")
        if not tech_stack:
            tech_stack.append("Static")
        
        tech_str = "+".join(tech_stack)
        
        print(f"{dep['app_name']:<20} {dep['instance_name']:<25} {dep['app_type']:<10} {tech_str:<15}")
    
    print("\n" + "=" * 60)
    print("📊 DETAILED DEPLOYMENT INFORMATION")
    print("=" * 60)
    
    for dep in deployments:
        print(f"\n🔧 {dep['app_name'].upper()}")
        print(f"   Config File: {dep['config_file']}")
        print(f"   Instance Name: {dep['instance_name']}")
        print(f"   Application Type: {dep['app_type']}")
        print(f"   OS Blueprint: {dep['blueprint']}")
        print(f"   Instance Size: {dep['bundle']}")
        print(f"   Health Endpoint: {dep['health_endpoint']}")
        print(f"   Expected Content: {dep['expected_content']}")
        
        # Technology stack
        print("   Technology Stack:")
        if dep["use_docker"]:
            print("     • Docker deployment")
        if dep["nginx_enabled"]:
            print("     • Nginx web server")
        if dep["nodejs_enabled"]:
            print("     • Node.js runtime")
        if dep["python_enabled"]:
            print("     • Python runtime")
        if dep["docker_enabled"] and not dep["use_docker"]:
            print("     • Docker available (not primary)")
    
    print("\n" + "=" * 60)
    print("🎯 INSTANCE NAMES FOR TROUBLESHOOTING")
    print("=" * 60)
    
    for dep in deployments:
        print(f"{dep['app_name']:<20} → {dep['instance_name']}")
    
    print("\n💡 Use these instance names with troubleshooting tools:")
    print("   • SSH access: ssh ubuntu@<instance-ip> or ssh ec2-user@<instance-ip>")
    print("   • AWS CLI: aws lightsail get-instance --instance-name <instance-name>")
    print("   • Troubleshooting scripts in troubleshooting-tools/ directory")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())