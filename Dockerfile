# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install all system dependencies for psycopg2, WeasyPrint, and general build
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        libpq-dev \
        libpango1.0-0 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        libcairo2 \
        libcairo2-dev \
        pkg-config \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libglib2.0-0 \
        libglib2.0-dev \
        libxml2 \
        libxslt1.1 \
        libjpeg-dev \
        zlib1g-dev \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 5000

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
