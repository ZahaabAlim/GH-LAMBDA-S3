import csv
import json
import boto3
import os
from datetime import datetime, timedelta

# Initialize AWS client for Cost Explorer
ce = boto3.client('ce')

def lambda_handler(event, context):
    # Define the time period for the report
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)

    # Format dates as strings
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Query AWS Cost Explorer for cost and usage
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date_str,
            'End': end_date_str
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'REGION'
            },
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )

    # Create a list to store CSV rows
    csv_rows = []
    csv_rows.append(['Date', 'Region', 'Service', 'Cost'])

    # Parse response data
    for result_by_time in response['ResultsByTime']:
        date = result_by_time['TimePeriod']['Start']
        for group in result_by_time['Groups']:
            region = group['Keys'][0]
            service = group['Keys'][1]
            cost = group['Metrics']['UnblendedCost']['Amount']
            csv_rows.append([date, region, service, cost])

    # Convert the list of lists to a CSV string
    csv_report = '\n'.join([','.join(row) for row in csv_rows])

    # Print the report to the Lambda logs
    print(csv_report)

    return {
        'statusCode': 200,
        'body': json.dumps('Report generated successfully')
    }
