# -*- coding: utf-8 -*-
#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Views for resource system, adding items, entering new categories for widgets etc
"""

import sys
import os

from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings

from django.template import RequestContext
from pile.views import *

from .mixins import *
from .models import *
from .forms import *

class GalleryMixin(object):
    pk_url_kwarg = 'gallery_id'
    model = Gallery

class DeleteGallery(GalleryMixin, OwnerUpdateMixin, DeleteView):
    pass

class CreateGallery(GalleryMixin, OwnerCreateMixin, CreateView):
    form_class = GalleryForm

class EditGallery(GalleryMixin, OwnerUpdateMixin, UpdateView):
    form_class = GalleryForm

class DeleteResource(OwnerUpdateMixin, DeleteView):
    model  = Resource
    action = "Delete Resource"

class EditResource(OwnerUpdateMixin, UpdateView):
    model = ResourceFile
    action = "Edit Resource"

    def get_form_class(self):
        category = getattr(self.object.category, 'id', 0)
        return FORMS.get(category, ResourceFileForm)

class PublishResource(OwnerUpdateMixin, DetailView):
    model = ResourceFile
    action = "Publish Resource"

    def post(self, request, *args, **kwargs):
        item = self.get_object()
        item.published = True
        item.save()
        return redirect("resource", item.pk)# Previously: redirect("gallery", item.gallery.id)

class MoveResource(EditResource):
    template_name = 'resource/resourcefile_move.html'

    # XXX todo - We need a form to show galleries


class UploadResource(OwnerCreateMixin, CreateView):
    form_class = ResourceFileForm
    model      = ResourceFile
    action     = "Upload New Resource"

    def form_valid(self, form):
        ret = super(UploadResource, self).form_valid(form)
        if hasattr(self, 'gallery'):
            self.gallery.items.add(form.instance)
        return ret


class DropResource(UploadResource):
    content_type  = 'text/plain'
    template_name = 'resource/ajax/add.txt'
    form_class    = ResourceAddForm

    def form_valid(self, form):
        ret = super(DropResource, self).form_valid(form)
        context = self.get_context_data(item=form.instance)
        return self.render_to_response(context)

class PasteIn(UploadResource):
    form_class = ResourcePasteForm


class ViewResource(DetailView):
    model = ResourceFile
    
    def get_queryset(self):
        qs = ResourceFile.objects.for_user(self.request.user)
        if 'username' in self.kwargs:
            return qs.filter(user__username=self.kwargs['username'])
        return qs

    def get(self, request, *args, **kwargs):
        ret = super(ViewResource, self).get(request, *args, **kwargs)
        if self.object.is_new:
            return redirect("edit_resource", self.object.pk)
        if request.user != self.object.user:
            if self.object.set_viewed(request.session) is None:
                raise ValueError("No Session Key found.")
        return ret

@login_required
def like_resource(request, pk, like):
    item = get_object_or_404(Resource, pk=pk)
    if item.user.pk == request.user.pk:
        raise PermissionDenied()

    if item.category.start_contest:
        # Some different rules for contest categories
        if item.category.start_contest > now().date():
            messages.warning(request, _('You may not vote until the contest begins.'))
            return redirect("resource", pk)
        if item.category.end_contest and item.category.end_contest < now().date():
            messages.warning(request, _('You may not vote after the contest ends.'))
            return redirect("resource", pk)
        votes = item.category.votes.filter(voter=request.user)
        if votes.count() > 0 and '+' in like:
            for vote in votes:
                vote.delete()
            if votes.filter(resource_id=item.id).count() == 0:
                messages.info(request, _('Your previous vote in this contest has been replaced by your vote for this item.'))

    (obj, is_new) = item.votes.get_or_create(voter=request.user)
    if '+' not in like:
        obj.delete()
    elif is_new == True and item.category.start_contest:
        messages.info(request, _('Thank you for your vote!'))
    return redirect("resource", pk)
    
def down_readme(request, pk):
    item = get_object_or_404(Resource, id=pk)
    return render_to_response('resource/readme.txt', {'item': item},
      context_instance=RequestContext(request),
      content_type="text/plain")

from sendfile import sendfile

class DownloadResource(ViewResource):
    template_name = 'resource/view_text.html'

    def get(self, request, *args, **kwargs):
        fn = kwargs.get('fn', None)
        item = self.get_object()
        # The view 'download' allows one to view an image in full screen glory
        # which is technically a download, but we count it as a view and try
        # and let the browser deal with showing the file.
        if fn is None:
            if item.mime().is_text():
                return super(DownloadResource, self).get(request, *args, **kwargs)
            item.fullview += 1
            item.save()
            return redirect(item.download.url)

        if fn not in ['download/', item.filename()]:
            messages.warning(request, _('Can not find file \'%s\', please retry download.' % fn))
            return redirect(item.get_absolute_url())

        # Otherwise the user intends to download the file and we record it as
        # such before passing the download path to nginx for delivery using a
        # content despatch to force the browser into saving-as.
        item.downed += 1
        item.save()

        # If the item is mirrored, then we need to select a good mirror to use
        if item.mirror:
            mirror = ResourceMirror.objects.select_mirror(item.edited)
            if mirror:
                response = render_to_response('resource/mirror-item.html', {
                     'mirror': mirror,
                     'item': item,
                     'url': mirror.get_url(item),
                   }, context_instance=RequestContext(request))
                response['refresh'] = "3; url=%s" % mirror.get_url(item)
                return response
        return redirect(item.download.url)

    # Content-Disposition code here allows downloads to work better. XXX
    # The thinking here is that it must a) redirect to a fastly cache just
    # Like the above, BUT include the attachment sendfile part to improve
    # user experence for images and similar files.
    #url = item.download.path
    #if not settings.DEBUG:
        # Correct for nginx redirect
        #url =  '/get' + url[6:]
    #return sendfile(request, url, attachment=True)


def mirror_resources(request, uuid=None):
    mirror = get_object_or_404(ResourceMirror, uuid=uuid) if uuid else None
    c = {
      'mirror'     : mirror,
      'items'      : ResourceFile.objects.filter(mirror=True),
      'now'        : now(),
      'mirrors'    : ResourceMirror.objects.all(),
    }
    if mirror:
        mirror.do_sync()
    return render_to_response('resource/mirror.html', c,
        context_instance=RequestContext(request))


def mirror_resource(request, uuid, filename):
    mirror = get_object_or_404(ResourceMirror, uuid=uuid)
    item = get_object_or_404(ResourceFile, download=os.path.join('resources', 'file', filename))
    url = item.download.path
    if not settings.DEBUG:
        # Correct for nginx redirect
        url =  '/get' + url[6:]
    return sendfile(request, url, attachment=True)



class MirrorAdd(CreateView):
    model      = ResourceMirror
    form_class = MirrorAddForm


class GalleryList(CategoryListView):
    rss_view = 'resources_rss'
    model = ResourceFile
    opts = (
      ('username', 'user__username'),
    )
    cats = (
      #('media_type', _("Media Type")),
      #('license', _("License")),
      ('category', _("Media Category")),
      ('galleries', _("User Gallery"), 'get_galleries'),
    )
    orders = (
      ('-liked', _('Most Popular')),
      ('-viewed', _('Most Views')),
      ('-downed', _('Most Downloaded')),
      ('-edited', _('Last Updated')),
    )

    def base_queryset(self):
        qs = super(GalleryList, self).base_queryset()
        if self.get_value('username') != self.request.user.username:
            qs = qs.filter(published=True)
        return qs

    def get_galleries(self):
        username = self.get_value('username')
        if username:
            return User.objects.get(username=username).galleries.filter(group__isnull=True)
        return None

    def get_context_data(self, **kwargs):
        data = super(GalleryList, self).get_context_data(**kwargs)
        if data.get('galleries', None) is not None:
             data['object'] = data['galleries']
        elif data.get('username', None):
             data['object'] = self.request.user
             data['action'] = "InkSpace"
        else:
            data['action'] = "InkSpaces"
        return data


class GalleryFeed(CategoryFeed, GalleryList):
    title = "Gallery Feed"
    description = "Gallery Resources RSS Feed"

    def items(self):
        for item in self.get_queryset():
            if hasattr(item, 'object'):
                item = item.object
            if callable(item):
                item = item()
            if item.is_visible():
                yield item

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description()

    def item_guid(self, item):
        return '#'+str(item.pk)

    def item_author_name(self, item):
        return str(item.user)

    def item_author_link(self, item):
        return item.user.get_absolute_url()

    def item_pubdate(self, item):
        return item.created

    def item_updateddate(self, item):
        return item.edited

