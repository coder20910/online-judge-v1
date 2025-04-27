FROM python:3.10-slim

# Environment variables first
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=online_judge.settings

# Set working directory
WORKDIR /app

# Install system dependencies including C++ tools
RUN apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the actual project files AFTER installing dependencies (for caching)
COPY . .

# Create directory for code execution
RUN mkdir -p /app/code_execution && \
    chmod 777 /app/code_execution

# Expose Django dev server port
EXPOSE 8000

# Start server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
