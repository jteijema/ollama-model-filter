# Use an official Python runtime as the base image
FROM python:3.10-slim

# Install curl and other dependencies
RUN apt-get update && apt-get install -y curl

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn if not in requirements.txt
RUN pip install --no-cache-dir gunicorn

# Expose the application port
EXPOSE 5000

# Add Docker HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Run the Flask app using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.app:app"]
