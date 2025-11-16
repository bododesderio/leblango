# 🛡️ Backup & Monitoring Setup Guide

## 📦 1. BACKUP STRATEGY

### Setup Instructions:

#### A. Install Backup Command

```bash
# 1. Create management command directory
mkdir -p backend/core/management/commands

# 2. Create __init__.py files
touch backend/core/management/__init__.py
touch backend/core/management/commands/__init__.py

# 3. Copy backup_db.py to:
#    backend/core/management/commands/backup_db.py

# 4. Copy backup scripts to project root:
#    - backup-db.sh
#    - restore-db.sh
#    - setup-backup-cron.sh

# 5. Make scripts executable
chmod +x backup-db.sh restore-db.sh setup-backup-cron.sh
```

#### B. Test Backup (Manual)

```bash
# Run backup from host
docker exec leblango_backend_container python manage.py backup_db

# Or run backup script
docker exec leblango_backend_container /app/backup-db.sh

# Check backup files
docker exec leblango_backend_container ls -lh /app/backups/
```

#### C. Setup Automated Backups

```bash
# Install cron in Docker container (add to Dockerfile)
# RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Setup cron jobs
docker exec leblango_backend_container /app/setup-backup-cron.sh

# View cron logs
docker exec leblango_backend_container tail -f /var/log/backup.log
```

#### D. Restore from Backup

```bash
# List available backups
docker exec leblango_backend_container ls -lh /app/backups/

# Restore specific backup
docker exec -it leblango_backend_container /app/restore-db.sh /app/backups/leblango_backup_20250113_020000.sql.gz
```

### Backup Schedule:

- **Daily**: 2:00 AM (kept for 7 days)
- **Weekly**: Sunday 3:00 AM (kept for 30 days)

### Backup Location:

- Container: `/app/backups/`
- Docker Volume: `backup_data`
- To access from host: `docker cp leblango_backend_container:/app/backups/ ./local-backups/`

---

## 📊 2. SENTRY MONITORING

### Setup Instructions:

#### A. Sign up for Sentry

```bash
# 1. Go to https://sentry.io
# 2. Create account (free tier available)
# 3. Create new "Django" project
# 4. Copy your DSN (looks like: https://xxx@sentry.io/123)
```

#### B. Install Sentry SDK

```bash
# 1. Add to backend/requirements.txt:
sentry-sdk[django]==2.18.0

# 2. Rebuild container
docker compose down
docker compose up -d --build
```

#### C. Configure Sentry

```bash
# 1. Add Sentry code to backend/leblango/settings.py
#    (Copy content from settings_sentry.py to end of settings.py)

# 2. Add to .env:
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_RELEASE=v1.0.0

# 3. Restart containers
docker compose restart leblango_backend_app
```

#### D. Test Sentry

```bash
# Test error capturing
docker exec leblango_backend_container python manage.py shell << 'EOF'
from sentry_sdk import capture_exception
try:
    1 / 0
except Exception as e:
    capture_exception(e)
    print("Test error sent to Sentry!")
EOF

# Check Sentry dashboard for the error
```

### Sentry Features:

- ✅ **Error Tracking**: Automatic exception capture
- ✅ **Performance Monitoring**: API endpoint speed tracking
- ✅ **Release Tracking**: Track errors by version
- ✅ **User Context**: See which users hit errors
- ✅ **Breadcrumbs**: See what led to an error
- ✅ **Alerts**: Email/Slack notifications on errors

---

## 🏥 3. ENHANCED HEALTH CHECKS

### Setup Instructions:

#### A. Update Health Check Views

```bash
# Replace backend/core/views_health.py with views_health_enhanced.py
```

#### B. Update URLs

```python
# In backend/leblango/urls.py, add:
from core.views_health import healthz, health_detail, readiness, liveness

urlpatterns = [
    path('healthz/', healthz),              # Basic health check
    path('health/', health_detail),         # Detailed health check
    path('readiness/', readiness),          # Kubernetes readiness probe
    path('liveness/', liveness),            # Kubernetes liveness probe
    # ... rest of URLs
]
```

#### C. Test Health Endpoints

```bash
# Basic health
curl http://localhost:6200/healthz/

# Detailed health (checks DB + Redis)
curl http://localhost:6200/health/

# Readiness probe
curl http://localhost:6200/readiness/

# Liveness probe
curl http://localhost:6200/liveness/
```

---

## 🚀 4. PRODUCTION DEPLOYMENT CHECKLIST

### Before Deploying:

- [ ] Sentry DSN configured in .env
- [ ] Backup cron jobs set up
- [ ] Test backup and restore process
- [ ] Health checks passing
- [ ] Monitor Sentry dashboard for errors
- [ ] Set up alerts in Sentry (email/Slack)
- [ ] Document backup restoration procedure
- [ ] Test error tracking with sample error

### Monitoring Dashboard:

1. **Sentry**: https://sentry.io (error tracking)
2. **Logs**: `docker logs leblango_backend_container`
3. **Backup Status**: `docker exec leblango_backend_container tail -f /var/log/backup.log`
4. **Health**: http://your-domain.com/health/

---

## 📝 QUICK REFERENCE

### Backup Commands

```bash
# Manual backup
docker exec leblango_backend_container python manage.py backup_db

# List backups
docker exec leblango_backend_container ls -lh /app/backups/

# Restore backup
docker exec -it leblango_backend_container /app/restore-db.sh /app/backups/file.sql.gz

# Download backup to local machine
docker cp leblango_backend_container:/app/backups/ ./local-backups/
```

### Monitoring Commands

```bash
# View Sentry errors in real-time
# Go to: https://sentry.io/organizations/your-org/issues/

# Check application health
curl http://localhost:6200/health/

# View logs
docker logs -f leblango_backend_container

# Check Redis
docker exec leblango_redis_container redis-cli ping

# Check PostgreSQL
docker exec leblango_postgres_container psql -U leblango -c "SELECT version();"
```

---

## 🎯 SUCCESS CRITERIA

You'll know everything is working when:

- ✅ Daily backups appear in `/app/backups/`
- ✅ Sentry dashboard shows your project
- ✅ Health checks return 200 OK
- ✅ Test errors appear in Sentry
- ✅ Backup restoration works
- ✅ Alerts configured in Sentry

---

**🎉 Your backend now has enterprise-grade backup and monitoring!**
