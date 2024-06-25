import json
import boto3
import csv
import os
from datetime import datetime
from io import StringIO

# Initialize AWS clients
ec2 = boto3.client('ec2')
sns = boto3.client('sns')
# SNS topic ARN (replace with your actual SNS topic ARN)
sns_topic_arn = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    # Get list of all regions
    all_regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
    # Extract instance status information
    instance_status_data = []
    for region in all_regions:
        # Initialize a new EC2 resource object in the specified region
        ec2_region = boto3.client('ec2', region_name=region)
        # Query EC2 instances in the current region
        response = ec2_region.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_state = instance['State']['Name']
                instance_type = instance['InstanceType']
                instance_az = instance['Placement']['AvailabilityZone']
                instance_name = ''
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                instance_status_data.append({
                    'Name': instance_name,
                    'InstanceId': instance_id,
                    'Status': instance_state,
                    'Region': instance_az,
                    'InstanceType': instance_type
                })

    # Convert the data to CSV format
    csv_buffer = StringIO()
    csv_writer = csv.DictWriter(csv_buffer, fieldnames=['Name', 'InstanceId', 'Status', 'Region', 'InstanceType'])
    csv_writer.writeheader()
    csv_writer.writerows(instance_status_data)
    csv_output = csv_buffer.getvalue()

    # Print the CSV report to the Lambda logs
    print(csv_output)

    # Publish the report to the SNS topic
    sns.publish(
        TopicArn=sns_topic_arn,
        Subject='EC2 Instance Status Report (CSV)',
        Message=csv_output
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Report generated and published successfully')
    }
