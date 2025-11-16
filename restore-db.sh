#!/bin/bash
# restore-db.sh - Restore PostgreSQL database from backup
# Usage: ./restore-db.sh <backup-file.sql.gz>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup-file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh /app/backups/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Configuration
DB_NAME="${POSTGRES_DB:-leblango}"
DB_USER="${POSTGRES_USER:-leblango}"
DB_PASSWORD="${POSTGRES_PASSWORD}"
DB_HOST="${DB_HOST:-postgres_db}"
DB_PORT="${DB_PORT:-5432}"

echo "=========================================="
echo "PostgreSQL Database Restoration"
echo "=========================================="
echo "⚠️  WARNING: This will replace the current database!"
echo "Database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "Backup file: $BACKUP_FILE"
echo "=========================================="
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restoration cancelled."
    exit 0
fi

# Export password
export PGPASSWORD="$DB_PASSWORD"

# Decompress if needed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "Decompressing backup..."
    TEMP_FILE="/tmp/restore_temp.sql"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    RESTORE_FILE="$TEMP_FILE"
else
    RESTORE_FILE="$BACKUP_FILE"
fi

# Restore database
echo "Restoring database..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$RESTORE_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Database restored successfully!"
else
    echo "❌ Restoration failed"
    exit 1
fi

# Clean up temp file
if [ -f "$TEMP_FILE" ]; then
    rm "$TEMP_FILE"
fi

# Unset password
unset PGPASSWORD

echo "=========================================="
echo "✅ Restoration complete!"
echo "=========================================="
