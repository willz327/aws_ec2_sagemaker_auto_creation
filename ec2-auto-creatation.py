"""
File: ec2-auto-create.py
Author: John Pan, Will Zhao
Last Modified: 2025-04-17

AWS EC2 Instance Creation Automation Script

Usage:
    python ec2-auto-create.py -t INSTANCE_TYPE -c COUNT

Required Environment Variables:
    AWS_ACCESS_KEY_ID: Your AWS access key ID
    AWS_SECRET_ACCESS_KEY: Your AWS secret access key

Arguments:
    -t, --instance-type INSTANCE_TYPE  EC2 instance type (e.g. g5.12xlarge)
    -c, --count COUNT                  Number of instances to create (default: 1)
    -i, --retry-interval INTERVAL      Retry interval in seconds (default: 10)
    -r, --max-retry MAX                Number of max retry times(default: 10)

Examples:
    # Basic usage with default retry interval (10 seconds)
    python ec2-auto-create.py -t g5.12xlarge -c 2
    
    # Custom retry interval of 15 seconds
    python ec2-auto-create.py -t g5.12xlarge -c 2 -i 15 -r 20
    
    # Minimal configuration example
    python ec2-auto-create.py --instance-type t2.micro --count 1 

Error Handling:
    - Retries for common AWS API errors with exponential backoff
    - Exits with error code 1 for critical failures

DISCLAIMER: This code is provided for educational and informational purposes only.
It should not be used in production environments without proper review, testing,
and modification to suit your specific needs. The author(s) and provider(s) of
this code assume no responsibility for any damages or losses that may arise from
the use of this code.

Features:
- Automated EC2 instance creation with retry logic
- Exponential backoff for API error handling
- Configurable through environment variables
"""
import os
import time
import argparse

import boto3
from botocore.exceptions import ClientError

# Constants (UPPER_CASE_WITH_UNDERSCORES)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Configuration (should be moved to config file or environment variables in production)
AMI_ID = "ami-xxx"  # Amazon Machine Image ID
KEY_PAIR_NAME = "xxx"           # SSH key pair name
SECURITY_GROUP_IDS = ["sg-xxx"]  # Security group IDs
SUBNET_ID = "subnet-xxx"          # VPC subnet ID
TAG_KEY = "demo"                # Resource tag key
TAG_VALUE = "true"              # Resource tag value
SNS_TOPIC_ARN = "arn:aws-cn:sns:xxx"  # SNS topic arn


def create_ec2_client(access_key: str, secret_key: str) -> boto3.client:
    """Create and configure EC2 client with AWS credentials."""
    return boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    ).client('ec2')

def handle_api_errors(error: ClientError, instance_type: str) -> bool:
    """Handle common EC2 API errors with appropriate retry logic."""
    error_code = error.response['Error']['Code']
    retry_errors = {
        'IdempotentParameterMismatch': 'Safe to retry immediately',
        'InsufficientInstanceCapacity': f'Insufficient capacity for {instance_type}',
        'RequestLimitExceeded': 'AWS API request limit exceeded',
        'ServiceUnavailable': 'EC2 service unavailable',
        'Unsupported': f'Instance type {instance_type} not supported'
    }

    if error_code in retry_errors:
        print(f"{retry_errors[error_code]}, retrying...")
        return True
    print(f"Unhandled error code: {error_code}")
    return False

def launch_instances(
    ec2_client: boto3.client,
    instance_type: str,
    target_count: int,
    retry_interval: int,
    max_retry: int
) -> None:
    """Launch EC2 instances with retry logic and exponential backoff."""
    instances_remaining = target_count
    retry_attempts = 0
    
    # 创建SNS客户端
    sns_client = boto3.client('sns',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    while instances_remaining > 0 and retry_attempts < max_retry:
        try:
            response = ec2_client.run_instances(
                ImageId=AMI_ID,
                InstanceType=instance_type,
                MinCount=1,
                MaxCount=1,
                KeyName=KEY_PAIR_NAME,
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': TAG_KEY, 'Value': TAG_VALUE}]
                }],
                SubnetId=SUBNET_ID,
                SecurityGroupIds=SECURITY_GROUP_IDS
            )
            
            instance_id = response['Instances'][0]['InstanceId']
            print(f'Successfully launched instance {instance_id}')
            print(f'Remaining instances: {instances_remaining-1}/{target_count}')
            
            # 发送SNS通知
            try:
                sns_client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Message=f"EC2 instance successfully launched!\nInstance ID: {instance_id}\nInstance Type: {instance_type}",
                    Subject=f"EC2 Instance {instance_id} Launch Notification"
                )
                print(f"Launch notification sent for instance {instance_id}")
            except Exception as sns_error:
                print(f"Failed to send notification: {str(sns_error)}")
            
            instances_remaining -= 1
            retry_attempts = 0  # Reset retry counter after success
            
        except ClientError as e:
            retry_attempts += 1
            if not handle_api_errors(e, instance_type):
                raise  # Re-raise unhandled errors
                
            print(f'Retrying in {retry_interval} seconds (attempt {retry_attempts}/{max_retry})')
            time.sleep(retry_interval)

def main() -> None:
    """Main execution flow with command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Automate EC2 instance creation with retry logic')
    parser.add_argument('-t', '--instance-type', required=True,
                        help='EC2 instance type (e.g. g5.12xlarge)')
    parser.add_argument('-c', '--count', type=int, default=1,
                        help='Number of instances to create (default: 1)')
    parser.add_argument('-i', '--retry-interval', type=int, default=10,
                        help='Retry interval in seconds (default: 10)')
    parser.add_argument('-r', '--max-retry', type=int, default=10,
                        help='Max retry (default: 10)')
    
    args = parser.parse_args()
    
    if args.count < 1:
        print("Error: Instance count must be at least 1")
        exit(1)

    ec2 = create_ec2_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    
    try:
        launch_instances(
            ec2_client=ec2,
            instance_type=args.instance_type,
            target_count=args.count,
            retry_interval=args.retry_interval,
            max_retry=args.max_retry
        )
    except Exception as e:
        print(f'Critical error: {str(e)}')
        exit(1)

if __name__ == '__main__':
    main()
