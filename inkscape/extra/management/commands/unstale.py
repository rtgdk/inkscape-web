from django.core.management.base import BaseCommand
from django.db.models import get_models, get_app
from django.contrib.auth.management import create_permissions

from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    args = '<app app ...>'
    help = 'reloads permissions for specified apps, or all apps if no args are specified'

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 0)
        models = get_models()
        labels = args or [ model._meta.app_label for model in models ]

        cts = ContentType.objects.exclude(app_label__in=labels)
        if raw_input("Delete %d stale content types? [y/N]: " % cts.count()).lower() == 'y':
            # This should delete most old permissions too.
            cts.delete()

        for label in labels:
            create_permissions(get_app(label), models, verbosity)


