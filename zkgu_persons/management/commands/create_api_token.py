from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from zkgu_persons.authentication import generate_api_token

class Command(BaseCommand):
    help = 'Create API token for user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username')

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options['username'])
            token = generate_api_token(user)
            self.stdout.write(
                self.style.SUCCESS(f'API Token: {token}')
            )
            self.stdout.write(
                self.style.SUCCESS('Сохраните токен - он больше не будет показан!')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Пользователь {options["username"]} не найден')
            )