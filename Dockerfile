# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

# Make port 2543 available to the world outside this container
EXPOSE 2543

# Define environment variable
ENV NAME myenv
ENV FLASK_ENV=dev

# Run app.py when the container launches
CMD ["python", "./app.py"]
