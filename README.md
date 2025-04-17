# AWS EC2/SageMaker Endpoint Auto Creation Scripts

This repository contains automation scripts for creating AWS resources (EC2 instances and SageMaker endpoints) with retry logic and notification features.

## Scripts

### 1. EC2 Auto Creation (`ec2-auto-creation.py`)

Automatically creates G5 series EC2 instances with retry logic and SNS notifications.

#### Features
- Automated EC2 instance creation with configurable retry logic
- Exponential backoff for API error handling
- SNS email notifications upon successful instance creation
- Support for multiple instance creation
- Configurable through command line arguments

#### Usage
```bash
# Basic usage with default retry interval (10 seconds)
python ec2-auto-creation.py -t g5.12xlarge -c 2

# Custom retry interval of 15 seconds and max retry of 20
python ec2-auto-creation.py -t g5.12xlarge -c 2 -i 15 -m 20

# Minimal configuration example
python ec2-auto-creation.py --instance-type t2.micro --count 1
```

#### Arguments
- `-t, --instance-type`: EC2 instance type (e.g., g5.12xlarge)
- `-c, --count`: Number of instances to create (default: 1)
- `-i, --retry-interval`: Retry interval in seconds (default: 10)
- `-m, --max-retry`: Number of max retry times (default: 10)

### 2. SageMaker Endpoint Auto Creation (`sagemaker-auto-creation.py`)

Automates the creation of SageMaker endpoints with retry logic and SNS notifications.

#### Features
- Automated SageMaker endpoint creation
- Endpoint configuration management
- Retry logic for API errors
- SNS email notifications upon successful endpoint creation
- Cleanup of resources on failure

#### Usage
```bash
# Basic usage
python sagemaker-auto-creation.py -m my-model -t ml.m5.large

# With custom retry settings
python sagemaker-auto-creation.py --model-name my-model --instance-type ml.m5.large --retry-interval 15 --max-retries 20
```

#### Arguments
- `-m, --model-name`: Name of the model to deploy
- `-t, --instance-type`: SageMaker instance type (e.g., ml.m5.large)
- `-i, --retry-interval`: Retry interval in seconds (default: 10)
- `-r, --max-retries`: Maximum number of retry attempts (default: 10)

## Prerequisites

### Environment Variables
Both scripts require AWS credentials to be set as environment variables:
```bash
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
```

### SNS Topic Setup
1. Create an SNS topic in your AWS account
2. Add email subscriptions to the topic
3. Confirm the subscription via email
4. Update the `SNS_TOPIC_ARN` in both scripts with your actual SNS topic ARN

### Required Python Packages
```bash
pip install boto3
```

## Error Handling

Both scripts include robust error handling:
- Retries for common AWS API errors
- Exponential backoff strategy
- Resource cleanup on failure
- Detailed error logging

## Security Considerations

- Store AWS credentials securely
- Use appropriate IAM roles and permissions
- Never commit credentials to version control
- Review and adjust security group settings for EC2 instances
- Monitor AWS CloudTrail logs for API activity

## Disclaimer

This code is provided for educational and informational purposes only. It should not be used in production environments without proper review, testing, and modification to suit your specific needs. The author(s) and provider(s) of this code assume no responsibility for any damages or losses that may arise from its use.

## License

[MIT License](LICENSE)
