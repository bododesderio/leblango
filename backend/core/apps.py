from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """
        Ensure required auth groups exist after migrations.

        Uses lazy import so it only runs once apps are ready
        and avoids AppRegistryNotReady in Docker.
        """
        from django.contrib.auth.models import Group  # imported lazily

        def create_groups(sender, **kwargs):
            for role in ("manager", "editor"):
                Group.objects.get_or_create(name=role)

        post_migrate.connect(create_groups, sender=self)
