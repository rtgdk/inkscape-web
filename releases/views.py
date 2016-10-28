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
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Platform, Release, ReleasePlatform, CACHE, Q

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
        # A selected release MUST have a release date AND must either
        # have no parent at all, or the parent MUST also have a release date
        qs = Release.objects.filter(release_date__isnull=False)
        qs = qs.filter(Q(parent__isnull=True) | Q(parent__release_date__isnull=False))
        release = qs.latest()
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
        selected = self.object
        (REVS, VERS, DEVEL) = range(3)
        (NAME, LIST, LATEST) = range(3)
        data['releases'] = [
            (_('Revisions'), [], 0),
            (_('Versions'), [], 1),
            (_('In Development'), [], 1),
        ]
        for rel in list(Release.objects.for_parent(self.object)):
            # The parent id is none, so this must be a top level release
            # Like 0.91 or 0.48 etc. pre-releases and point releases will
            # have a parent_id of their master release.
            if rel.parent_id is None:
                if rel.release_date:
                    # This is a released 'master release' (Versions)
                    data['releases'][VERS][LIST].append(rel)
                else:
                    # This is an unreleased master release (in development)
                    data['releases'][DEVEL][LIST].append(rel)
                # This is the selected release or the parent of it (revisions)
                if rel.pk == selected.parent_id or rel.pk == selected.pk:
                    data['releases'][REVS][LIST].append(rel)
            else:
                # This is a point or pre-release add to 'revisions'
                data['releases'][REVS][LIST].append(rel)

        if len(data['releases'][REVS][LIST]) == 1:
            # Empty the revisions list if it's just one item
            data['releases'][REVS][LIST].pop()

        # Hide pre-release revisions if the master release is 'released'
        # We first record where in the ordered list the master release is
        # and flag if it's been released. Items that happen /after/ that
        # are pre-releases.
        is_released = False

        # When we find the spot in the list, we then want to have already
        # worked out if the selected item happened 'before' it. That way
        # selecting a pre-release will show up and won't be hidden.
        is_before = False

        for item in data['releases'][REVS][LIST]:
            if is_released:
                # If the parent is released and the selected is before
                # tell the html to hide this item (we can use js to enable)
                item.hide = True
                data['has_pre_releases'] = True

            if item.pk == selected.pk and not is_released:
                # The selected item happens /before/ the parent/master
                # (or is the parent/master) and thus we can hide pre releases.
                is_before = True

            if item.parent_id is None and item.release_date and is_before:
                # This item is the parent/master, all items below are pre.
                is_released = True

        if self.request.GET.get('latest', False):
            data['object'] = selected.latest

        data['platforms'] = self.object.platforms.for_level('')
        return data



class PlatformList(ReleaseView):
    template_name = 'releases/platform_list.html'

    def get_title(self):
        return _('All Platforms for %s') % unicode(self.object)


class PlatformView(DetailView):
    model = Platform
    slug_field = 'codename'
    slug_url_kwarg = 'platform'

    def get_context_data(self, **kwargs):
        data = super(PlatformView, self).get_context_data(**kwargs)
        obj = self.object

        data['release'] = get_object_or_404(Release, version=self.kwargs['version'])
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
        return get_object_or_404(self.model,
            release__version=self.kwargs['version'],
            platform__codename=self.kwargs['platform']
          )

