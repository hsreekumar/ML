FROM public.ecr.aws/lambda/python:3.12

# Install dependencies
RUN pip install --no-cache-dir scikit-learn joblib


# Copy function code into the container
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your Lambda handler function
CMD ["lambda_function.lambda_handler"]