# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install required packages
RUN pip install --no-cache-dir scikit-learn joblib fastapi uvicorn boto3 numpy python-multipart

# Copy the app code
COPY main.py .

# Expose the port FastAPI will run on
EXPOSE 8000

# Run FastAPI server with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
