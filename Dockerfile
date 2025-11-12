FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements from backend
COPY backend/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy backend project into image
COPY backend /app/backend
COPY django.sh /django.sh
RUN chmod +x /django.sh

# All Django commands run from here
WORKDIR /app/backend

EXPOSE 6200

CMD ["/django.sh"]
