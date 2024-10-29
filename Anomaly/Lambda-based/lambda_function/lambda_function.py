import boto3
import joblib
import tarfile
import os
from io import BytesIO
from sklearn.cluster import KMeans
import json
import numpy as np

s3_client = boto3.client('s3')

def get_latest_model(bucket, prefix):
    """Retrieve the latest model.tar.gz file from S3"""
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    # Find the model.tar.gz file
    for content in response.get('Contents', []):
        if content['Key'].endswith('model.tar.gz'):
            print(f"Model found at: {content['Key']}")
            return content['Key']
    raise FileNotFoundError("No model.tar.gz found in the specified S3 path")

def load_model_from_s3(bucket, model_s3_path):
    """Load the model file from S3 and extract the joblib file"""
    # Download model.tar.gz from S3
    with BytesIO() as model_buffer:
        print(f"Downloading model from S3: s3://{bucket}/{model_s3_path}")
        s3_client.download_fileobj(bucket, model_s3_path, model_buffer)
        model_buffer.seek(0)
        
        # Extract the tar.gz file to get the model
        with tarfile.open(fileobj=model_buffer, mode='r:gz') as tar:
            print(f"Extracting model to /tmp")
            tar.extractall(path="/tmp")
    
    # Load the model
    model = joblib.load("/tmp/kmeans_model.joblib")
    print("Model loaded successfully")
    return model

def calculate_distance(point, cluster_center):
    """Calculate the Euclidean distance between a point and a cluster center"""
    return np.linalg.norm(np.array(point) - np.array(cluster_center))

def lambda_handler(event, context):
    try:
        # Define your bucket and prefix (could be passed from event)
        bucket = 'anomaly-price'
        prefix = 'kmeans-output/output'  # General prefix for the models

        # Get the latest model path from S3
        model_s3_path = get_latest_model(bucket, prefix)
        print(f"Loading model from: s3://{bucket}/{model_s3_path}")

        # Load the model
        kmeans_model = load_model_from_s3(bucket, model_s3_path)
        
        # Log the incoming event data
        print(f"Event received: {event}")

        # Your anomaly detection logic here...
        event_data = event['data']
        print(f"Data for prediction: {event_data}")

        # Perform prediction
        cluster_assignment = kmeans_model.predict([event_data])[0]  # Example prediction
        print(f"Assigned cluster: {cluster_assignment}")

        # Get the cluster center for the assigned cluster
        cluster_center = kmeans_model.cluster_centers_[cluster_assignment]
        print(f"Cluster center: {cluster_center}")

        # Calculate the distance to the cluster center
        distance = calculate_distance(event_data, cluster_center)
        print(f"Distance from cluster center: {distance}")

        # Define a distance threshold for anomaly detection (this can be tuned based on your data)
        threshold = 10.0  # Example threshold value
        is_anomaly = distance > threshold
        print(f"Is anomaly: {is_anomaly}")

        # Convert boolean to string for JSON serialization
        return {
            'statusCode': 200,
            'body': json.dumps({
                'cluster': int(cluster_assignment),
                'distance': distance,
                'is_anomaly': str(is_anomaly).lower()  # Convert boolean to string ("true" or "false")
            })
        }

    except Exception as e:
        # Log the error and return a failure response
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }