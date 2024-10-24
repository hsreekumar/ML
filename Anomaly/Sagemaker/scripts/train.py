import subprocess
import sys

# Install s3fs to allow pandas to read from S3
subprocess.check_call([sys.executable, "-m", "pip", "install", "s3fs"])
import os
import joblib
import pandas as pd
import boto3
from sklearn.cluster import KMeans

def copy_model_to_final_location(model_path, bucket, target_key):
    """Helper function to copy model to the final S3 location"""
    s3 = boto3.client('s3')

    # Upload model to final location
    s3.upload_file(model_path, bucket, target_key)
    print(f"Model copied to s3://{bucket}/{target_key}")

def train_kmeans(data_path, n_clusters):
    print(f"Data path: {data_path}, n_clusters: {n_clusters}")

    # Load dataset from S3 path
    data = pd.read_csv(data_path)
    print(f"Loaded data: {data.head()}")

    # Train KMeans model
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(data[['price']].values)
    print("KMeans training complete.")

    # Model output path (local)
    model_output_dir = os.getenv('SM_MODEL_DIR', '/opt/ml/model')
    model_path = os.path.join(model_output_dir, 'kmeans_model.joblib')
    
    # Save the model locally first
    joblib.dump(kmeans, model_path)
    print(f"Model saved locally at: {model_path}")

    # Copy the model to the final desired location
    bucket = 'anomaly-price'
    target_key = 'kmeans-output/output/model.tar.gz'  # Final desired location

    # Compress and upload model directly
    compressed_model_path = os.path.join(model_output_dir, 'model.tar.gz')
    joblib.dump(kmeans, '/opt/ml/model/kmeans_model.joblib')  # Save joblib model locally
    os.system(f'tar -czvf {compressed_model_path} -C {model_output_dir} kmeans_model.joblib')  # Compress the model

    # Upload to the desired S3 location
    copy_model_to_final_location(compressed_model_path, bucket, target_key)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', type=str, default='s3://anomaly-price/events.csv')
    parser.add_argument('--n-clusters', type=int, default=5)

    args = parser.parse_args()
    
    train_kmeans(args.data_path, args.n_clusters)