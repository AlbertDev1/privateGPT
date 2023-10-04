# Use an official Python runtime as a parent image
FROM python:3.11


RUN apt update && apt upgrade -y
RUN apt install -y build-essential

# Set the working directory in Docker to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Do not copy the data inside source_documents
#RUN rm -rf /app/source_documents/*

# Install required packages using requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app to listen on
EXPOSE 5000

# Define an entrypoint to run your Flask app using python
ENTRYPOINT ["python", "api.py"]
