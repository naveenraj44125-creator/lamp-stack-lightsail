#!/usr/bin/env python3
"""
Create a new AWS Lightsail instance for testing the reusable workflow
"""

import boto3
import sys
import time

def create_lightsail_instance():
    """Create a new Lightsail instance"""
    
    # Configuration
    instance_name = "example-app-instance"
    region = "us-east-1"
    availability_zone = "us-east-1a"
    blueprint_id = "ubuntu_22_04"
    bundle_id = "nano_3_0"  # $3.50/month
    
    print("🚀 Creating Lightsail Instance")
    print("=" * 60)
    print(f"Instance Name: {instance_name}")
    print(f"Region: {region}")
    print(f"Blueprint: {blueprint_id}")
    print(f"Bundle: {bundle_id}")
    print("=" * 60)
    
    try:
        # Create Lightsail client
        client = boto3.client('lightsail', region_name=region)
        
        # Check if instance already exists
        try:
            response = client.get_instance(instanceName=instance_name)
            print(f"✅ Instance '{instance_name}' already exists!")
            print(f"State: {response['instance']['state']['name']}")
            print(f"Public IP: {response['instance'].get('publicIpAddress', 'N/A')}")
            return
        except client.exceptions.NotFoundException:
            print(f"📝 Instance '{instance_name}' does not exist. Creating...")
        
        # Create the instance
        response = client.create_instances(
            instanceNames=[instance_name],
            availabilityZone=availability_zone,
            blueprintId=blueprint_id,
            bundleId=bundle_id,
            userData="""#!/bin/bash
# Initial setup script
apt-get update
apt-get install -y python3-pip
echo "Instance created successfully" > /tmp/instance-ready
"""
        )
        
        print(f"✅ Instance creation initiated!")
        print(f"Operation ID: {response['operations'][0]['id']}")
        
        # Wait for instance to be running
        print("\n⏳ Waiting for instance to be running...")
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(10)
            try:
                instance = client.get_instance(instanceName=instance_name)
                state = instance['instance']['state']['name']
                print(f"   Attempt {attempt + 1}/{max_attempts}: State = {state}")
                
                if state == 'running':
                    print("\n✅ Instance is now running!")
                    print(f"Public IP: {instance['instance'].get('publicIpAddress', 'N/A')}")
                    break
            except Exception as e:
                print(f"   Checking... {e}")
        
        # Create and attach static IP
        print("\n🌐 Creating static IP...")
        static_ip_name = f"{instance_name}-static-ip"
        
        try:
            ip_response = client.allocate_static_ip(staticIpName=static_ip_name)
            static_ip = ip_response['operations'][0]['resourceName']
            print(f"✅ Static IP allocated: {static_ip_name}")
            
            # Wait a bit before attaching
            time.sleep(5)
            
            # Attach static IP to instance
            attach_response = client.attach_static_ip(
                staticIpName=static_ip_name,
                instanceName=instance_name
            )
            print(f"✅ Static IP attached to instance")
            
            # Get the static IP address
            ip_info = client.get_static_ip(staticIpName=static_ip_name)
            static_ip_address = ip_info['staticIp']['ipAddress']
            
            print("\n" + "=" * 60)
            print("🎉 Instance Created Successfully!")
            print("=" * 60)
            print(f"Instance Name: {instance_name}")
            print(f"Static IP: {static_ip_address}")
            print(f"Region: {region}")
            print("\n📝 Update your deployment-generic.config.yml with:")
            print(f"  instance_name: {instance_name}")
            print(f"  static_ip: {static_ip_address}")
            print("=" * 60)
            
        except client.exceptions.AlreadyExistsException:
            print(f"⚠️  Static IP '{static_ip_name}' already exists")
            ip_info = client.get_static_ip(staticIpName=static_ip_name)
            static_ip_address = ip_info['staticIp']['ipAddress']
            print(f"Static IP Address: {static_ip_address}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_lightsail_instance()
