import boto3
import joblib
import tarfile
import os
from io import BytesIO
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
import logging

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize S3 client
s3_client = boto3.client('s3')
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
        bucket = 'anomaly-price'
        model_s3_path = get_latest_model(bucket, 'kmeans-output/output')
        kmeans_model = load_model_from_s3(bucket, model_s3_path)
    return kmeans_model

class PredictionRequest(BaseModel):
    data: list

@app.post("/predict")
async def predict(request: PredictionRequest):
    """Endpoint for making predictions"""
    logger.info(f"Received prediction request with data: {request.data}")
    
    kmeans_model = get_model()
    
    # Access the data from the request object
    data = request.data
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
            'distance': float(distance),  # Convert to float for JSON serialization
            'is_anomaly': bool(is_anomaly)  # Ensure it is a bool
        }
    
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return {"error": "Prediction failed"}, 500