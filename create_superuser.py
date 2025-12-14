import os
import django
from django.contrib.auth import get_user_model
from django.conf import settings

# Initialize Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticket_manager.settings")
django.setup()

User = get_user_model()

def create_superuser():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not all([username, email, password]):
        print("Skipping superuser creation: Missing environment variables.")
        return

    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists. Skipping.")
    else:
        print(f"Creating superuser '{username}'...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created successfully!")

if __name__ == "__main__":
    create_superuser()
