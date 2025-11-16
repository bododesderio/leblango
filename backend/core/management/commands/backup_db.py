# backend/core/management/commands/backup_db.py
"""
Django management command for database backups.
Usage: python manage.py backup_db
"""

import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Create a PostgreSQL database backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='/app/backups',
            help='Directory to store backups (default: /app/backups)'
        )
        parser.add_argument(
            '--retention-days',
            type=int,
            default=7,
            help='Number of days to keep backups (default: 7)'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            default=True,
            help='Compress backup with gzip (default: True)'
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output_dir'])
        retention_days = options['retention_days']
        compress = options['compress']

        # Create backup directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get database config
        db_config = settings.DATABASES['default']
        db_name = db_config['NAME']
        db_user = db_config['USER']
        db_password = db_config['PASSWORD']
        db_host = db_config['HOST']
        db_port = db_config['PORT']

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = output_dir / f"{db_name}_backup_{timestamp}.sql"

        self.stdout.write("=" * 50)
        self.stdout.write(self.style.SUCCESS('PostgreSQL Backup'))
        self.stdout.write("=" * 50)
        self.stdout.write(f"Database: {db_name}")
        self.stdout.write(f"Host: {db_host}:{db_port}")
        self.stdout.write(f"Output: {backup_file}")
        self.stdout.write("=" * 50)

        # Set environment for pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password

        # Build pg_dump command
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-d', db_name,
            '--no-owner',
            '--no-acl',
            '--clean',
            '--if-exists',
            '-f', str(backup_file)
        ]

        try:
            # Run backup
            self.stdout.write("Creating backup...")
            subprocess.run(cmd, env=env, check=True, capture_output=True)
            self.stdout.write(self.style.SUCCESS(f"✅ Backup created: {backup_file}"))

            # Compress if requested
            if compress:
                self.stdout.write("Compressing backup...")
                subprocess.run(['gzip', str(backup_file)], check=True)
                backup_file_gz = Path(f"{backup_file}.gz")
                size_mb = backup_file_gz.stat().st_size / (1024 * 1024)
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Backup compressed: {backup_file_gz} ({size_mb:.2f} MB)"
                ))
                final_file = backup_file_gz
            else:
                size_mb = backup_file.stat().st_size / (1024 * 1024)
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Backup size: {size_mb:.2f} MB"
                ))
                final_file = backup_file

            # Clean up old backups
            self.stdout.write(f"Cleaning up backups older than {retention_days} days...")
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0

            for old_backup in output_dir.glob(f"{db_name}_backup_*.sql*"):
                if old_backup.stat().st_mtime < cutoff_date.timestamp():
                    old_backup.unlink()
                    deleted_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"✅ Deleted {deleted_count} old backup(s)"
            ))

            # List current backups
            backups = sorted(output_dir.glob(f"{db_name}_backup_*.sql*"))
            self.stdout.write("\nCurrent backups:")
            for backup in backups:
                size = backup.stat().st_size / (1024 * 1024)
                mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                self.stdout.write(f"  - {backup.name} ({size:.2f} MB, {mtime})")

            self.stdout.write("")
            self.stdout.write("=" * 50)
            self.stdout.write(self.style.SUCCESS("✅ Backup completed successfully!"))
            self.stdout.write("=" * 50)

        except subprocess.CalledProcessError as e:
            raise CommandError(f"Backup failed: {e.stderr.decode() if e.stderr else str(e)}")
        except Exception as e:
            raise CommandError(f"Backup failed: {str(e)}")
