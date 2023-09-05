from django.core.management.base import BaseCommand

from blogging.helpers import create_system_roles


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_system_roles()
