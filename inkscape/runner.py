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

import shutil
import tempfile

from django.conf import settings

from django.test.runner import DiscoverRunner

class MediaManagerMixin(object):
    """Mixin to create MEDIA_ROOT in temp and tear down when complete."""

    def setup_test_environment(self):
        super(MediaManagerMixin, self).setup_test_environment()
        self._temp_media = tempfile.mkdtemp()
        # We don't backup or restore the original values, because tests should
        # never really be looking at the normal media_root
        settings.MEDIA_ROOT = self._temp_media
        settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    def teardown_test_environment(self):
        super(MediaManagerMixin, self).teardown_test_environment()
        shutil.rmtree(self._temp_media, ignore_errors=True)

class InkscapeTestSuiteRunner(MediaManagerMixin, DiscoverRunner):
    pass

