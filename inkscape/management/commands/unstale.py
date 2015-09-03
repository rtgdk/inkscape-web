#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom 
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#

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


