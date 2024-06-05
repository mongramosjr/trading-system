from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a regular user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('email', type=str, help='Email address of the user')
        parser.add_argument('password', type=str, help='Password of the user')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        email = kwargs['email']
        password = kwargs['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR('Username already exists'))
        else:
            User.objects.create_user(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'User {username} created successfully'))
