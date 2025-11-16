# Generated migration for adding trigram indexes
# Save as: backend/core/migrations/0008_add_trigram_indexes.py

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations
from django.contrib.postgres.indexes import GinIndex


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_enable_pg_trgm'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='dictionaryentry',
            index=GinIndex(
                fields=['lemma'],
                name='lemma_trgm_idx',
                opclasses=['gin_trgm_ops']
            ),
        ),
        migrations.AddIndex(
            model_name='dictionaryentry',
            index=GinIndex(
                fields=['gloss_ll'],
                name='gloss_ll_trgm_idx',
                opclasses=['gin_trgm_ops']
            ),
        ),
        migrations.AddIndex(
            model_name='dictionaryentry',
            index=GinIndex(
                fields=['gloss_en'],
                name='gloss_en_trgm_idx',
                opclasses=['gin_trgm_ops']
            ),
        ),
    ]
