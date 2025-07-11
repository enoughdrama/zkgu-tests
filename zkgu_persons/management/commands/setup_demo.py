from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from zkgu_persons.authentication import generate_api_token

class Command(BaseCommand):
    help = 'Setup demo user and API token'

    def handle(self, *args, **options):
        # Создать демо пользователя
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@zkgu.local',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created demo user: {user.username}')
            )
        
        # Создать API токен
        token = generate_api_token(user)
        
        self.stdout.write(
            self.style.SUCCESS('=== SETUP COMPLETE ===')
        )
        self.stdout.write(f'Username: {user.username}')
        self.stdout.write(f'Password: demo123')
        self.stdout.write(f'API Token: {token}')
        self.stdout.write(
            self.style.WARNING('Save this token! Copy it to your browser localStorage.')
        )
        self.stdout.write(
            'Open browser console and run:'
        )
        self.stdout.write(
            f"localStorage.setItem('apiToken', '{token}')"
        )