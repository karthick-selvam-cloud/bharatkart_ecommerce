FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/ /app/requirements/
RUN pip install --upgrade pip
RUN pip install -r requirements/base.txt
RUN pip install -r requirements/ml.txt

# Copy project
COPY . /app/

# Create directories
RUN mkdir -p /app/media /app/staticfiles /app/logs /app/chroma_db /app/faiss_index

# Run collectstatic
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "ecommerce.asgi:application"]