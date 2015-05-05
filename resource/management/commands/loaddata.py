#
# Copyright 2013 Duncan Ingram, Inc. (MIT License)
#           2015 Martin Owens (AGPLv3)
#
# See LICENSE for details
#
"""
Overloads django's loaddata command so it will install media fixtures
These are colelctions of files ready to be used with database entries
for example FileField and ImageField.
"""

from os.path import dirname, exists, isdir, join, relpath

from django.conf import settings
import django.core.management.commands.loaddata
from django.core.files.storage import default_storage
import django.core.serializers
from django.db.models import get_apps, get_models, signals
from django.db.models.fields.files import FileField
from django.utils._os import upath


# For Python < 3.3
file_not_found_error = getattr(__builtins__,'FileNotFoundError', IOError)


def models_with_filefields():
    for app in get_apps():
        klasses = get_models(app)
        for klass in klasses:
            if any(isinstance(field, FileField) for field in klass._meta.fields):
                yield klass

GLOBAL_WARN = set()

class Command(django.core.management.commands.loaddata.Command):

    def load_images_for_signal(self, sender, **kwargs):
        not_found = set()
        is_found  = set()

        instance = kwargs['instance']
        for field in sender._meta.fields:
            if not isinstance(field, FileField):
                continue
            path = getattr(instance, field.attname)
            if path is None or not path.name:
                continue
            for fixture_path in self.fixture_media_paths:
                filepath = join(fixture_path, path.name)
                try:
                    with open(filepath, 'rb') as f:
                        default_storage.save(path.name, f)
                        is_found.add(path.name)
                        break
                except file_not_found_error:
                    not_found.add(path.name)

        for filename in (not_found - is_found):
            if filename not in GLOBAL_WARN:
                self.stderr.write(" [skipping] Expected file: %s" % filepath)
                GLOBAL_WARN.add(filename)

    def handle(self, *fixture_labels, **options):
        # Hook up pre_save events for all the apps' models that have FileFields.
        for klass in models_with_filefields():
            signals.pre_save.connect(self.load_images_for_signal, sender=klass)

        fixture_paths = self.find_fixture_paths()
        fixture_paths = (join(path, 'media') for path in fixture_paths)
        fixture_paths = [path for path in fixture_paths if isdir(path)]
        self.fixture_media_paths = fixture_paths

        ret = super(Command, self).handle(*fixture_labels, **options)

        # Disconnect all the signals
        for klass in models_with_filefields():
            signals.pre_save.disconnect(self.load_images_for_signal, sender=klass)

        return ret

    def find_fixture_paths(self):
        """Return the full paths to all possible fixture directories."""
        app_module_paths = []
        for app in get_apps():
            if hasattr(app, '__path__'):
                # It's a 'models/' subpackage
                for path in app.__path__:
                    app_module_paths.append(upath(path))
            else:
                # It's a models.py module
                app_module_paths.append(upath(app.__file__))

        app_fixtures = [join(dirname(path), 'fixtures') for path in app_module_paths]

        return app_fixtures + list(settings.FIXTURE_DIRS)
