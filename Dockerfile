# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY agent.py api.py index.html get_voices.py mock_data.py ./
COPY assets/ ./assets/
COPY rag/ ./rag/

# Make startup script executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose Flask port
EXPOSE 5001

CMD ["/start.sh"]
