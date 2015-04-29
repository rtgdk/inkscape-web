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

