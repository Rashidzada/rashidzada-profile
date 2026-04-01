import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a Django superuser from arguments or environment variables if one does not already exist."

    def add_arguments(self, parser):
        parser.add_argument("--username", dest="username", help="Superuser username")
        parser.add_argument("--email", dest="email", help="Superuser email")
        parser.add_argument("--password", dest="password", help="Superuser password")

    def handle(self, *args, **options):
        username = (options.get("username") or os.getenv("DJANGO_SUPERUSER_USERNAME", "")).strip()
        email = (options.get("email") or os.getenv("DJANGO_SUPERUSER_EMAIL", "")).strip()
        password = (options.get("password") or os.getenv("DJANGO_SUPERUSER_PASSWORD", "")).strip()

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping superuser creation because DJANGO_SUPERUSER_USERNAME or "
                    "DJANGO_SUPERUSER_PASSWORD is not set."
                )
            )
            return

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists."))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
