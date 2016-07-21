# -*- coding: utf-8 -*-
#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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
Provide news mixins
"""

from datetime import date

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from django.utils import dateformat
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache

from cms.utils import get_language_from_request

from .models import News

class PublishedNewsMixin(object):
    """
    Since the queryset also has to filter elements by timestamp
    we have to fetch it dynamically.
    """
    date_field = 'pub_date'
    month_format = '%m'

    def get_language(self):
        return get_language_from_request(self.request)

    def get_queryset(self):
        return News.published.with_language(self.get_language(),
            is_staff=self.request.user.has_perm('cmsplugin_news.change_news'))

    def get_breadcrumb_root(self):
        result = []
        result.append((reverse('news:archive_index'), _('News')))
        if 'year' in self.kwargs:
            kw = {'year': self.kwargs['year']}
            result.append((reverse('news:archive_year', kwargs=kw), kw['year']))
            if 'month' in self.kwargs:
                kw['month'] = self.kwargs['month']
                dt = date(int(kw['year']), int(kw['month']), int(self.kwargs.get('day', 1)))
                title = dt.strftime('%B')
                result.append((reverse('news:archive_month', kwargs=kw), title))
                if 'day' in self.kwargs:
                    kw['day'] = self.kwargs['day']
                    title = dateformat.format(dt, 'jS')
                    result.append((reverse('news:archive_day', kwargs=kw), title))
        elif 'pk' in self.kwargs:
            result.append((None, _('Unpublished')))
        return result


class NeverCacheMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)

