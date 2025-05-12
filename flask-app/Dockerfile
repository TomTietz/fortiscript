# Use official Python base image
# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install required packages
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port 5000 for the Flask application
EXPOSE 5000

# Run the application
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]