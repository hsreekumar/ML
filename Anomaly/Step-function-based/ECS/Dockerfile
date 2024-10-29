# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install required packages
RUN pip install --no-cache-dir scikit-learn joblib boto3 numpy python-multipart

# Copy the app code
COPY main.py .

# Define the command to run the script
CMD ["python", "main.py"]
