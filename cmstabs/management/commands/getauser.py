#
# Copyright Martin Owens 2013
#
# AGPLv3
#
"""
Returns the id for a single user. This is used to migrate backups for use locally.
"""

from django.contrib.auth.models import User

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = ''
    help = 'Returns the first valid user\'s id to the command line.'

    def handle(self, *args, **options):
        for user in User.objects.all():
            # TODO: In the future we can check validity here.
            print user.id
            return
        raise ValueError("No valid user is available for use.")

