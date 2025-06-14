# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
# Even if empty, it's good practice for consistency
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# This step will be quick if requirements.txt is empty
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# This includes app.py and README.md
COPY . .

# No EXPOSE needed if it's primarily a batch job or internal worker without an API yet

# Define environment variables
ENV PYTHONUNBUFFERED 1
ENV SERVICE_NAME AI-Processing-Service

# Run app.py when the container launches
CMD ["python", "app.py"]
