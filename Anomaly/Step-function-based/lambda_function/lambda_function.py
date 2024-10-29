import boto3
import logging

# Initialize boto3 clients
sqs_client = boto3.client('sqs')

# Constants
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/339712893183/eventQ.fifo'

def lambda_handler(event, context):
    """Lambda function to check SQS queue size without consuming messages"""
    # Check queue attributes to get the approximate number of messages
    response = sqs_client.get_queue_attributes(
        QueueUrl=SQS_QUEUE_URL,
        AttributeNames=['ApproximateNumberOfMessages']
    )
    
    # Retrieve the message count from the response
    message_count = int(response['Attributes'].get('ApproximateNumberOfMessages', 0))
    
    return {
        'batch_size': message_count,
        'messages': []  # Keeping an empty list for compatibility
    }