# Define the AWS provider and region
provider "aws" {
  region = "us-east-1"
}
# Configure the Terraform backend to store the state in S3 and use DynamoDB for locking
terraform {
  backend "s3" {
    bucket = "tf-backend-st1"
    key    = "terraform.tfstate"
    region = "us-east-1"
 
    dynamodb_table = "TfStatelock"
  }
}
# Create an AWS Lambda function
resource "aws_lambda_function" "example" {
  function_name = "upload_lambda"  # Name of the Lambda function

  s3_bucket = var.s3_bucket  # S3 bucket for deployment
  s3_key    = var.s3_key     # S3 key for deployment

  handler = var.lambda_handler  # Lambda function handler
  runtime = "python3.10"        # Python runtime version

  role = aws_iam_role.iam_for_lambda.arn  # ARN of the IAM role
}

# Create an IAM role for the Lambda function
resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"  # Name of the IAM role

  # Assume role policy allowing Lambda service to assume this role
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
