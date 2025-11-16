# Generated migration for enabling pg_trgm extension
# Save as: backend/core/migrations/0007_enable_pg_trgm.py

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_dictionaryentry_options_and_more'),
    ]

    operations = [
        # Create extension with IF NOT EXISTS to avoid errors in tests
        migrations.RunSQL(
            sql='CREATE EXTENSION IF NOT EXISTS pg_trgm;',
            reverse_sql='DROP EXTENSION IF EXISTS pg_trgm;',
        ),
    ]
