#!/bin/bash
# backup-db.sh - Automated PostgreSQL database backup script
# Usage: ./backup-db.sh
# Or schedule with cron: 0 2 * * * /path/to/backup-db.sh

set -e

# Configuration from environment or defaults
DB_NAME="${POSTGRES_DB:-leblango}"
DB_USER="${POSTGRES_USER:-leblango}"
DB_PASSWORD="${POSTGRES_PASSWORD}"
DB_HOST="${DB_HOST:-postgres_db}"
DB_PORT="${DB_PORT:-5432}"

# Backup directory
BACKUP_DIR="${BACKUP_DIR:-/app/backups}"
mkdir -p "$BACKUP_DIR"

# Retention policy (days)
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql"
BACKUP_FILE_GZ="${BACKUP_FILE}.gz"

echo "=========================================="
echo "PostgreSQL Backup Script"
echo "=========================================="
echo "Database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "Timestamp: $TIMESTAMP"
echo "=========================================="

# Export password for pg_dump
export PGPASSWORD="$DB_PASSWORD"

# Create backup
echo "Creating backup..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --no-owner --no-acl --clean --if-exists \
    -f "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_FILE"
    
    # Compress backup
    echo "Compressing backup..."
    gzip "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ Backup compressed: $BACKUP_FILE_GZ"
        
        # Calculate size
        SIZE=$(du -h "$BACKUP_FILE_GZ" | cut -f1)
        echo "📦 Backup size: $SIZE"
    else
        echo "❌ Failed to compress backup"
        exit 1
    fi
else
    echo "❌ Backup failed"
    exit 1
fi

# Clean up old backups (older than RETENTION_DAYS)
echo "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "${DB_NAME}_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
echo "✅ Cleanup complete"

# List current backups
echo ""
echo "Current backups:"
ls -lh "$BACKUP_DIR"/${DB_NAME}_backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo ""
echo "=========================================="
echo "✅ Backup completed successfully!"
echo "=========================================="

# Unset password
unset PGPASSWORD
