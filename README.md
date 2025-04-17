# AWS Resource Auto Creation Scripts

This repository contains automation scripts for creating AWS resources (EC2 instances and SageMaker endpoints) with retry logic and notification features.

## Setup and Installation

### 1. Python Environment
Ensure you have Python installed on your system. The scripts are compatible with Python 3.x.

### 2. Install Dependencies
Clone the repository and install the required packages:
```bash
# Clone the repository
git clone [repository-url]
cd [repository-name]

# Install dependencies
pip install -r requirements.txt
```

### 3. AWS Credentials
Set up your AWS credentials using one of these methods:

1. Environment variables:
```bash
export AWS_ACCESS_KEY_ID="your_access_key_id"
export AWS_SECRET_ACCESS_KEY="your_secret_access_key"
```

2. Or using AWS CLI configuration:
```bash
aws configure
```

### 4. SNS Topic Setup
1. Create an SNS topic in your AWS account
2. Add email subscriptions to the topic
3. Confirm the subscription via email
4. Update the `SNS_TOPIC_ARN` in the scripts with your actual SNS topic ARN

## Scripts

### 1. EC2 Auto Creation (`g5/ec2-auto-create.py`)

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
python ec2-auto-create.py -t g5.12xlarge -c 2

# Custom retry interval of 15 seconds and max retry of 20
python ec2-auto-create.py -t g5.12xlarge -c 2 -i 15 -m 20

# Minimal configuration example
python ec2-auto-create.py --instance-type t2.micro --count 1
```

#### Arguments
- `-t, --instance-type`: EC2 instance type (e.g., g5.12xlarge)
- `-c, --count`: Number of instances to create (default: 1)
- `-i, --retry-interval`: Retry interval in seconds (default: 10)
- `-m, --max-retry`: Number of max retry times (default: 10)

### 2. SageMaker Endpoint Auto Creation (`g5/sagemaker-auto-create.py`)

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
python sagemaker-auto-create.py -m my-model -t ml.m5.large

# With custom retry settings
python sagemaker-auto-create.py --model-name my-model --instance-type ml.m5.large --retry-interval 15 --max-retries 20
```

#### Arguments
- `-m, --model-name`: Name of the model to deploy
- `-t, --instance-type`: SageMaker instance type (e.g., ml.m5.large)
- `-i, --retry-interval`: Retry interval in seconds (default: 10)
- `-r, --max-retries`: Maximum number of retry attempts (default: 10)

## Configuration

### EC2 Configuration
The EC2 script uses the following configuration parameters that can be modified in the script:
- `AMI_ID`: Amazon Machine Image ID
- `KEY_PAIR_NAME`: SSH key pair name
- `SECURITY_GROUP_IDS`: Security group IDs
- `SUBNET_ID`: VPC subnet ID
- `TAG_KEY` and `TAG_VALUE`: Resource tags

### SageMaker Configuration
The SageMaker script requires:
- Pre-existing SageMaker model
- Valid instance type for deployment
- Proper IAM roles and permissions

## Error Handling

Both scripts include robust error handling:
- Retries for common AWS API errors
- Exponential backoff strategy
- Resource cleanup on failure
- Detailed error logging

## Monitoring and Notifications

### SNS Notifications
Both scripts send notifications via Amazon SNS when:
- EC2 instances are successfully created
- SageMaker endpoints are successfully deployed

Notification contents include:
- Resource IDs
- Instance types
- Creation timestamps
- Status information

## Security Considerations

- Store AWS credentials securely
- Use appropriate IAM roles and permissions
- Never commit credentials to version control
- Review and adjust security group settings for EC2 instances
- Monitor AWS CloudTrail logs for API activity
- Regularly rotate access keys
- Use VPC endpoints where possible
- Implement proper network security controls

## Troubleshooting

Common issues and solutions:
1. AWS credential errors
   - Verify environment variables are set correctly
   - Check AWS CLI configuration
   - Ensure IAM permissions are correct

2. Resource creation failures
   - Check service quotas and limits
   - Verify network connectivity
   - Review security group settings

3. SNS notification issues
   - Confirm SNS topic ARN is correct
   - Verify email subscription is confirmed
   - Check IAM permissions for SNS

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Disclaimer

This code is provided for educational and informational purposes only. It should not be used in production environments without proper review, testing, and modification to suit your specific needs. The author(s) and provider(s) of this code assume no responsibility for any damages or losses that may arise from its use.

## License

[MIT License](LICENSE)

## Support

For support, please:
1. Check the documentation
2. Review existing issues
3. Create a new issue with:
   - Detailed description of the problem
   - Error messages
   - Steps to reproduce
   - Environment details
