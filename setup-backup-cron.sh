#!/bin/bash
# setup-backup-cron.sh - Setup automated backups with cron
# Run this inside the backend container

set -e

echo "Setting up automated database backups..."

# Create cron job file
cat > /etc/cron.d/leblango-backup << 'EOF'
# Leblango Database Backup Cron Job
# Runs daily at 2:00 AM
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# Daily backup at 2 AM
0 2 * * * root cd /app/backend && /usr/local/bin/python manage.py backup_db --retention-days=7 >> /var/log/backup.log 2>&1

# Weekly backup (kept for 30 days) - Sundays at 3 AM
0 3 * * 0 root cd /app/backend && /usr/local/bin/python manage.py backup_db --retention-days=30 --output-dir=/app/backups/weekly >> /var/log/backup.log 2>&1
EOF

# Set proper permissions
chmod 0644 /etc/cron.d/leblango-backup

# Create log file
touch /var/log/backup.log
chmod 666 /var/log/backup.log

echo "✅ Cron job created: /etc/cron.d/leblango-backup"
echo ""
echo "Backup schedule:"
echo "  - Daily:  2:00 AM (kept for 7 days)"
echo "  - Weekly: 3:00 AM on Sundays (kept for 30 days)"
echo ""
echo "To test the backup now:"
echo "  docker exec leblango_backend_container python manage.py backup_db"
