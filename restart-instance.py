#!/usr/bin/env python3
"""
AWS Lightsail Instance Restart Script
Restarts a Lightsail instance using AWS credentials
"""

import boto3
import sys
import time
from botocore.exceptions import ClientError, NoCredentialsError

def restart_lightsail_instance(instance_name, region='us-east-1'):
    """
    Restart a Lightsail instance
    
    Args:
        instance_name (str): Name of the Lightsail instance
        region (str): AWS region where the instance is located
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create Lightsail client
        lightsail = boto3.client('lightsail', region_name=region)
        
        print(f"Attempting to restart instance: {instance_name}")
        
        # Get instance status first
        response = lightsail.get_instance(instanceName=instance_name)
        current_state = response['instance']['state']['name']
        print(f"Current instance state: {current_state}")
        
        # Restart the instance
        restart_response = lightsail.reboot_instance(instanceName=instance_name)
        
        if restart_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"✅ Restart command sent successfully for instance: {instance_name}")
            
            # Wait for instance to be running
            print("Waiting for instance to restart...")
            waiter = lightsail.get_waiter('instance_running')
            waiter.wait(
                instanceName=instance_name,
                WaiterConfig={
                    'Delay': 15,
                    'MaxAttempts': 40
                }
            )
            
            print(f"✅ Instance {instance_name} has been successfully restarted!")
            return True
        else:
            print(f"❌ Failed to restart instance: {instance_name}")
            return False
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS Error ({error_code}): {error_message}")
        return False
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please configure your credentials.")
        print("You can set them using:")
        print("  export AWS_ACCESS_KEY_ID=your_access_key")
        print("  export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("  export AWS_SESSION_TOKEN=your_session_token  # if using temporary credentials")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Main function"""
    # Default instance name - you can modify this or pass as argument
    instance_name = "lamp-stack-instance"
    region = "us-east-1"
    
    # Check if instance name provided as argument
    if len(sys.argv) > 1:
        instance_name = sys.argv[1]
    
    if len(sys.argv) > 2:
        region = sys.argv[2]
    
    print("🔄 AWS Lightsail Instance Restart Script")
    print("=" * 50)
    print(f"Account ID: 257429339749")
    print(f"Instance: {instance_name}")
    print(f"Region: {region}")
    print("=" * 50)
    
    success = restart_lightsail_instance(instance_name, region)
    
    if success:
        print("\n✅ Instance restart completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Instance restart failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
