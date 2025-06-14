# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# This includes app.py and .env.sample (but .env should be gitignored and not copied)
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables (can be overridden at runtime)
# FLASK_APP is already set in the .env.sample and typically loaded by python-dotenv
# However, it's good practice to set it for clarity if not using .env in container directly
ENV FLASK_APP app.py
# ENV FLASK_ENV production # Set this at runtime or in K8s deployment for production

# Run app.py when the container launches
# Using gunicorn for a more production-ready server is common,
# but flask run is simpler for this example and matches current app.py's __main__ block.
# For gunicorn, you'd add gunicorn to requirements.txt and use:
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
# For now, sticking to python app.py which uses Flask's development server.
# The app.py already has host='0.0.0.0' so it's accessible.
CMD ["python", "app.py"]
