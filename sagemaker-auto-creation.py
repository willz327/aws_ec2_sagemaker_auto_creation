"""
File: sagemaker-auto-create.py
Author: John Pan, Will Zhao
Last Modified: 2025-04-17

AWS SageMaker Endpoint Creation Automation Script

Usage:
    python sagemaker-auto-create.py -m MODEL_NAME -t INSTANCE_TYPE

Required Environment Variables:
    AWS_ACCESS_KEY_ID: Your AWS access key ID
    AWS_SECRET_ACCESS_KEY: Your AWS secret access key

Arguments:
    -m, --model-name MODEL_NAME      Name of the model to deploy
    -t, --instance-type INSTANCE_TYPE SageMaker instance type (e.g. ml.m5.large)
    -i, --retry-interval INTERVAL    Retry interval in seconds (default: 10)
    -r, --max-retries MAX_RETRIES    Maximum number of retry attempts (default: 10)

Examples:
    python sagemaker-auto-create.py -m my-model -t ml.m5.large
    python sagemaker-auto-create.py --model-name my-model --instance-type ml.m5.large --retry-interval 15

Error Handling:
    - Retries for common SageMaker API errors
    - Exits with error code 1 for critical failures

DISCLAIMER: This code is provided for educational and informational purposes only.
It should not used in production environments without proper review, testing,
and modification to suit your specific needs. The author(s) and provider(s) of
this code assume no responsibility for any damages or losses that may arise from
the use of this code.
"""
import os
import time
import argparse

import boto3
from botocore.exceptions import ClientError

# Constants
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Configuration (should be moved to config file or environment variables in production)
MAX_RETRIES = 10
RETRY_INTERVAL = 10
SNS_TOPIC_ARN = "arn:aws-cn:sns:xxx"  # sns topic arn

def create_sagemaker_client(access_key: str, secret_key: str) -> boto3.client:
    """Create and configure SageMaker client with AWS credentials."""
    return boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    ).client('sagemaker')

def config_exists(sagemaker_client: boto3.client, config_name: str) -> bool:
    """Check if an endpoint configuration exists."""
    try:
        sagemaker_client.describe_endpoint_config(EndpointConfigName=config_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            return False
        raise

def handle_api_errors(error: ClientError) -> bool:
    """Handle common SageMaker API errors with appropriate retry logic."""
    error_code = error.response['Error']['Code']
    retry_errors = {
        'ThrottlingException': 'API request throttled',
        'ServiceUnavailable': 'SageMaker service unavailable',
        'InternalFailure': 'Internal SageMaker service error'
    }

    if error_code in retry_errors:
        print(f"{retry_errors[error_code]}, retrying...")
        return True
    print(f"Unhandled error code: {error_code}")
    return False

def create_endpoint_config(
    sagemaker_client: boto3.client,
    model_name: str,
    instance_type: str,
    args: argparse.Namespace
) -> str:
    """Create SageMaker endpoint configuration with retry logic."""
    config_name = f"{model_name}-config"
    
    config_file_path = 'config.json'
    if os.path.exists(config_file_path):
        print(f"Config file {config_file_path} already exists. Please delete it first.")
        return None

    if config_exists(sagemaker_client, config_name):
        print(f"Endpoint configuration {config_name} already exists. Please delete it first.")
        return None

    try:
        response = sagemaker_client.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[{
                'VariantName': 'AllTraffic',
                'ModelName': model_name,
                'InstanceType': instance_type,
                'InitialInstanceCount': 1,
                'InitialVariantWeight': 1.0
            }]
        )
        print(f"Successfully created endpoint configuration: {config_name}")
        return config_name
    except ClientError as e:
        if not handle_api_errors(e):
            raise
        print(f'Failed to create endpoint configuration: {str(e)}')
    return None

def create_endpoint(
    sagemaker_client: boto3.client,
    model_name: str,
    config_name: str,
    args: argparse.Namespace
) -> None:
    """Create SageMaker endpoint with retry logic."""
    endpoint_name = f"{model_name}-endpoint"
    retry_attempts = 0
    
    while retry_attempts < args.max_retries:
        try:
            response = sagemaker_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=config_name,
                Tags=[{'Key': 'auto-created', 'Value': 'true'}]
            )
            print(f"Successfully created endpoint: {endpoint_name}")
            
            # 发送SNS通知
            try:
                sns_client = boto3.client('sns',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                )
                sns_client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Message=f"SageMaker endpoint successfully created!\nEndpoint Name: {endpoint_name}\nModel Name: {model_name}\nInstance Type: {args.instance_type}",
                    Subject=f"SageMaker Endpoint {endpoint_name} Creation Notification"
                )
                print(f"Creation notification sent for endpoint {endpoint_name}")
            except Exception as sns_error:
                print(f"Failed to send notification: {str(sns_error)}")
            
            return
            
        except ClientError as e:
            retry_attempts += 1
            if not handle_api_errors(e):
                # Clean up config if endpoint creation fails
                try:
                    sagemaker_client.delete_endpoint_config(EndpointConfigName=config_name)
                    print(f"Deleted endpoint configuration: {config_name}")
                except Exception as cleanup_error:
                    print(f"Failed to clean up config: {str(cleanup_error)}")
                raise
            print(f'Retrying endpoint creation in {args.retry_interval} seconds (attempt {retry_attempts}/{args.max_retries})')
            time.sleep(args.retry_interval)

def main() -> None:
    """Main execution flow with command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Automate SageMaker endpoint creation with retry logic')
    parser.add_argument('-m', '--model-name', required=True,
                        help='Name of the model to deploy')
    parser.add_argument('-t', '--instance-type', required=True,
                        help='SageMaker instance type (e.g. ml.m5.large)')
    parser.add_argument('-i', '--retry-interval', type=int, default=RETRY_INTERVAL,
                        help='Retry interval in seconds (default: 10)')
    parser.add_argument('-r', '--max-retries', type=int, default=MAX_RETRIES,
                        help='Maximum number of retry attempts (default: 10)')
    
    args = parser.parse_args()
    
    sagemaker = create_sagemaker_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    
    try:
        config_name = create_endpoint_config(
            sagemaker_client=sagemaker,
            model_name=args.model_name,
            instance_type=args.instance_type,
            args=args
        )
        
        if config_name:
            create_endpoint(
                sagemaker_client=sagemaker,
                model_name=args.model_name,
                config_name=config_name,
                args=args
            )
    except Exception as e:
        print(f'Critical error: {str(e)}')
        exit(1)

if __name__ == '__main__':
    main()
