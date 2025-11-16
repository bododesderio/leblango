# backend/core/tests/conftest.py
"""
Pytest fixtures for core tests.
Ensures PostgreSQL pg_trgm extension is available for fuzzy search tests.
"""
import pytest
from django.db import connection


@pytest.fixture(scope='session', autouse=True)
def enable_pg_trgm_extension(django_db_setup, django_db_blocker):
    """
    Ensure pg_trgm extension is enabled in test database.
    This runs once per test session before any tests.
    """
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            except Exception as e:
                # If extension creation fails, tests will fail gracefully
                # This can happen if test user doesn't have SUPERUSER privileges
                print(f"Warning: Could not create pg_trgm extension: {e}")
                print("Fuzzy search tests may fail. Grant SUPERUSER to test database user.")
