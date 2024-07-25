# Base image
FROM python:3.10-slim

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libpq-dev \
    libmariadb-dev-compat \ 
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
#RUN pip install -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code over
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]