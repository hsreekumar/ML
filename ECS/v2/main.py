import boto3
import joblib
import tarfile
import os
from io import BytesIO
import numpy as np
import logging
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize S3 and SQS clients
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')

# S3 and SQS configuration
SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/339712893183/eventQ.fifo'
RESULTS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/339712893183/Receiver.fifo'
S3_BUCKET = 'anomaly-price'
S3_PREFIX = 'kmeans-output/output'

kmeans_model = None  # Global variable to cache the model

def get_latest_model(bucket, prefix):
    """Retrieve the latest model.tar.gz file from S3"""
    logger.info(f"Fetching the latest model from S3 bucket: {bucket} with prefix: {prefix}")
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for content in response.get('Contents', []):
        if content['Key'].endswith('model.tar.gz'):
            logger.info(f"Model found at: {content['Key']}")
            return content['Key']
    logger.error("No model.tar.gz found in the specified S3 path")
    raise FileNotFoundError("No model.tar.gz found in the specified S3 path")

def load_model_from_s3(bucket, model_s3_path):
    """Load the model file from S3 and extract the joblib file"""
    with BytesIO() as model_buffer:
        logger.info(f"Downloading model from S3: s3://{bucket}/{model_s3_path}")
        s3_client.download_fileobj(bucket, model_s3_path, model_buffer)
        model_buffer.seek(0)
        
        with tarfile.open(fileobj=model_buffer, mode='r:gz') as tar:
            logger.info("Extracting model to /tmp")
            tar.extractall(path="/tmp")
    
    model = joblib.load("/tmp/kmeans_model.joblib")
    logger.info("Model loaded successfully")
    return model

def calculate_distance(point, cluster_center):
    """Calculate the Euclidean distance between a point and a cluster center"""
    distance = np.linalg.norm(np.array(point) - np.array(cluster_center))
    logger.info(f"Calculated distance: {distance} for point: {point} and cluster center: {cluster_center}")
    return distance

def get_model():
    """Load the model if not already loaded and return it"""
    global kmeans_model
    if kmeans_model is None:
        model_s3_path = get_latest_model(S3_BUCKET, S3_PREFIX)
        kmeans_model = load_model_from_s3(S3_BUCKET, model_s3_path)
    return kmeans_model

def predict(data):
    """Make prediction using KMeans model"""
    kmeans_model = get_model()
    logger.info(f"Data received for prediction: {data}")
    
    try:
        cluster_assignment = kmeans_model.predict([data])[0]
        logger.info(f"Predicted cluster assignment: {cluster_assignment}")

        cluster_center = kmeans_model.cluster_centers_[cluster_assignment]
        logger.info(f"Cluster center for assignment {cluster_assignment}: {cluster_center}")

        distance = calculate_distance(data, cluster_center)
        threshold = 10.0  # Set your threshold for anomaly detection
        is_anomaly = distance > threshold

        logger.info(f"Distance from cluster center: {distance}, Anomaly detected: {is_anomaly}")

        return {
            'cluster': int(cluster_assignment),
            'distance': float(distance),
            'is_anomaly': bool(is_anomaly)
        }
    
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return {"error": "Prediction failed"}

def send_result_to_sqs(result):
    """Send the prediction result to the results SQS queue"""
    try:
        # Generate a unique deduplication ID (e.g., based on current time or result content)
        deduplication_id = str(hash(json.dumps(result)))
        
        sqs_client.send_message(
            QueueUrl=RESULTS_QUEUE_URL,
            MessageBody=json.dumps(result),
            MessageGroupId="results_group",  # FIFO queues require a group ID
            MessageDeduplicationId=deduplication_id  # Unique ID for each message to avoid duplication error
        )
        logger.info(f"Result sent to SQS results queue: {result}")
    except Exception as e:
        logger.error(f"Failed to send result to SQS: {str(e)}")
        
def process_sqs_messages():
    """Poll messages from SQS and process them"""
    while True:
        response = sqs_client.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5  # Long polling
        )

        messages = response.get('Messages', [])
        
        if not messages:
            logger.info("No more messages in the queue. Exiting.")
            break

        for message in messages:
            try:
                # Parse message body
                message_body = json.loads(message['Body'])
                data = message_body['data']
                logger.info(f"Received message with data: {data}")

                # Make prediction
                result = predict(data)
                logger.info(f"Prediction result: {result}")

                # Send result to results queue
                send_result_to_sqs(result)

            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
            finally:
                # Delete message from queue after processing
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )

        time.sleep(1)  # Optional: Throttle the polling rate

if __name__ == "__main__":
    process_sqs_messages()