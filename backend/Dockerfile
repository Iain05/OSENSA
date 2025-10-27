# Backend Dockerfile: Python service that connects to Mosquitto via websockets
FROM python:3.12-slim

# Prevent Python from writing pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source
COPY . /app

# Default environment variables (can be overridden in docker-compose)
ENV BROKER=mosquitto
ENV PORT=9001

# If your app listens on a port for management, expose it (not strictly required for MQTT client)
EXPOSE 9001

# Run the main application
CMD ["python", "-u", "main.py"]
