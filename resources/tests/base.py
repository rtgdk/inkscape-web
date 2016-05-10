#
# Copyright 2016, Maren Hachmann <marenhachmann@yahoo.com>
#                 Martin Owens <doctormo@gmail.com>
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
"""
Base TestCase for Resource and Gallery Tests.
"""

# FLAG: do not report failures from here in tracebacks
# pylint: disable=invalid-name
__unittest = True

from autotest.base import HaystackMixin, ExtraTestCase

from resources.models import ResourceFile
from inkscape.middleware import AutoBreadcrumbMiddleware

class BaseCase(HaystackMixin, ExtraTestCase):
    fixtures = ['test-auth', 'licenses', 'categories', 'quota', 'resource-tests']

    def setUp(self):
        "Creates a dictionary containing a default post request for resources"
        super(BaseCase, self).setUp()
        self.groups = None
        if self.user:
            self.groups = self.user.groups.all()
        self.download = self.open('file5.svg')
        self.thumbnail = self.open('preview5.png')
        self.data = {
          'download': self.download,
          'thumbnail': self.thumbnail,
          'name': 'Test Resource Title',
          'link': 'http://www.inkscape.org',
          'desc': 'My nice picture',
          'category': 2,
          'license': 4,
          'owner': 'True',
          'published': 'on',
        }

    def tearDown(self):
        super(BaseCase, self).tearDown()
        self.download.close()
        self.thumbnail.close()

    def assertEndorsement(self, endorse=ResourceFile.ENDORSE_NONE, **kw):
        rec = ResourceFile.objects.filter(**kw)
        self.assertGreater(rec.count(), 0, "No resources with: %s" % str(kw))

        for resource in rec:
            self.assertEqual(resource.endorsement(), endorse,
                "Endorsement doesn't match for file: %s and sig %s" %
                (resource.download, resource.signature))


class BaseBreadcrumbCase(BaseCase):
    def assertBreadcrumbRequest(self, url, *terms, **kwargs):
        cont = self.assertGet(url, **kwargs).content
        crumbs = cont.split('breadcrumbs">', 1)[-1].split('</div>')[0]
        try:
            for x, term in enumerate(terms):
                if len(term) == 1:
                    self.assertIn('<em class="crumb">%s<' % term, crumbs)
                elif x == len(terms) - 1 and len(terms) != 1:
                    self.assertIn('<em class="crumb">%s<' % term[1], crumbs)
                else:
                    self.assertIn('href="%s" class="crumb">%s<' % term, crumbs)
        except AssertionError:
            raise AssertionError("Breadcrumb %s missing from %s" % (
                str(term), crumbs))

    def assertBreadcrumbs(self, obj, *terms, **kwargs):
        """Test breadcrumbs in both generation and template request"""
        crumbs = list(AutoBreadcrumbMiddleware()._crumbs(object=obj, **kwargs))
        (links1, names1) = zip(*crumbs)
        (links2, names2) = zip(*terms)
        # The i18n gets in the way of testing the names
        #self.assertTupleEqual(names1, names2)
        self.assertTupleEqual(links1, links2)
        if hasattr(obj, 'get_absolute_url'):
            self.assertBreadcrumbRequest(obj.get_absolute_url(), *terms)

