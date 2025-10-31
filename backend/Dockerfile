FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for pyttsx3
RUN apt-get update && apt-get install -y \
    espeak \
    libespeak-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create storage directory
RUN mkdir -p storage/snapshots storage/tts storage/whitelist

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
