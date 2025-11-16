FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps including PostgreSQL client tools for pg_dump
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements from backend
COPY backend/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy backend project into image
COPY backend /app/backend

# Copy backup scripts
COPY backup-db.sh /app/backup-db.sh
COPY restore-db.sh /app/restore-db.sh
COPY setup-backup-cron.sh /app/setup-backup-cron.sh
RUN chmod +x /app/*.sh

# Copy Django startup script
COPY django.sh /django.sh
RUN chmod +x /django.sh

# All Django commands run from here
WORKDIR /app/backend

EXPOSE 6200

CMD ["/django.sh"]
