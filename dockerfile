# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for OpenCV and DeepFace
# libgl1 is the modern replacement for libgl1-mesa-glx
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Create the uploads directory and set permissions
# This ensures the app can save the analyzed images without "Permission Denied" errors
RUN mkdir -p /app/static/uploads && chmod -R 777 /app/static

# Hugging Face Spaces requires the app to live on port 7860
EXPOSE 7860

# Run the app using Gunicorn
# --timeout 120 gives the AI models time to process
# --preload loads the app before forking worker processes (better for memory)
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "120", "--preload", "app:app"]