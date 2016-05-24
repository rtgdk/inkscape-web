# -*- coding: utf-8 -*-
#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
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

from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView
from django.views.generic import ListView, DetailView
from django.conf import settings

from .models import Platform, Release, ReleasePlatform, CACHE

class DownloadRedirect(RedirectView):
    """Attempts to redirect the user to the right page for their os"""
    permanent = False

    def get_redirect_url(self, *args, **kw):
        (family, version, bits) = self.get_os()
        key = slugify('download-%s-%s' % (family, str(version)))
        if bits:
            key += '-%d' % bits

        url = None #CACHE.get(key)
        if not url:
            url = self.get_url(family, version, bits)
            CACHE.set(key, url, 2 * 3600) # Two hours

        if settings.DEBUG:
            url += '?os=' + key

        return url

    def get_url(self, family, version, bits=None):
        release = Release.objects.filter(release_date__isnull=False).latest()
        platforms = list(release.platforms.for_os(family, version, bits))

        if len(platforms) == 1:
            return platforms[0].get_absolute_url()
        elif len(set([p.platform.parent for p in platforms])) == 1:
            return platforms[0].parent.get_absolute_url()
        return release.get_absolute_url()

    def get_os(self):
        # We would use user_agent parsing, but to fair, it's dreadful at os
        # giving enough data for very basic stats, but not for downloads.
        ua = self.request.META.get('HTTP_USER_AGENT', '').lower()

        if 'windows' in ua:
            bits = 64 if 'wow64' in ua or 'win64' in ua else 32
            version = ua.split(' nt ', 1)[-1].split(';', 1)[0]
            return ('Windows', version, bits)
        elif 'mac os x' in ua:
            version = ua.split('mac os x ')[-1].split(';')[0].replace('_', '.')
            # Limit to a single decimal version (e.g. 10.9.3 -> 10.9)
            version = version.rsplit('.', version.count('.') - 1)[0]
            return ('Mac OS X', version, 64)
        elif 'linux' in ua:
            bits = ua.split('linux')[-1].split(';')[0]
            bits = 64 if '64' in bits else 32
            version = None
            for distro in ('ubuntu', 'fedora', 'debian', 'arch'):
                if distro in ua:
                    version = distro
            return ('Linux', version, bits)

        return ('Unknown', None, None)


class ReleaseList(ListView):
    template_name = 'releases/release_detail.html'
    model = Release


class ReleaseView(DetailView):
    cache_tracks = (Release, Platform)
    model = Release
    slug_field = 'version'
    slug_url_kwarg = 'version'

    def get_context_data(self, **kwargs):
        data = super(ReleaseView, self).get_context_data(**kwargs)
        data['releases'] = [
            (_('Other Revisions'), [], 0),
            (_('Versions'), [], 1),
            (_('In Development'), [], 1),
        ]
        for rel in list(Release.objects.for_parent(self.object)):
            if rel.parent_id is None:
                if rel.release_date:
                    data['releases'][1][1].append(rel)
                else:
                    data['releases'][2][1].append(rel)
                if rel.pk == self.object.parent_id or rel.pk == self.object.pk:
                    data['releases'][0][1].append(rel)
            else:
                data['releases'][0][1].append(rel)
        if len(data['releases'][0][1]) == 1:
            data['releases'][0][1].pop()
        if self.request.GET.get('latest', False):
            data['object'] = self.object.latest

        data['platforms'] = self.object.platforms.for_level('')
        return data



class PlatformList(ListView):
    queryset = Platform.objects.filter(parent__isnull=True)


class PlatformView(DetailView):
    model = Platform
    slug_field = 'codename'
    slug_url_kwarg = 'platform'

    def get_context_data(self, **kwargs):
        data = super(PlatformView, self).get_context_data(**kwargs)
        obj = self.object

        data['release'] = Release.objects.get(version=self.kwargs['version'])
        data['platforms'] = data['release'].platforms.for_level(obj.codename)
        data['platform'] = data['object']

        try:
            data['object'] = data['release'].platforms.get(platform__codename=obj.codename)
        except ReleasePlatform.DoesNotExist:
            data['object'] = ReleasePlatform(release=data['release'], platform=data['platform'])
        except ReleasePlatform.MultipleObjectsReturned:
            data['object'] = None

        return data


class ReleasePlatformView(DetailView):
    title = _('Download Started')
    model = ReleasePlatform

    def get_object(self):
        return self.model.objects.get(
            release__version=self.kwargs['version'],
            platform__codename=self.kwargs['platform']
        )
