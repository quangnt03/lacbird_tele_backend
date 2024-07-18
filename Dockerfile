# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src

# Copy the current directory contents into the container at /usr/src
COPY . /usr/src

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 80 for the app
EXPOSE 80

# Run uvicorn server with the specified application
ENTRYPOINT ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "80"]