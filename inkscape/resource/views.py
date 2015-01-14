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
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.utils.timezone import now
from django.contrib.auth.models import User
from pile.views import breadcrumbs

from .models import *
from .forms import *

@login_required
def delete_gallery(request, gallery_id):
    item = get_object_or_404(Gallery, id=gallery_id, user=request.user)
    if request.method == 'POST':
        if 'confirm' in request.POST:
            item.delete()
        return redirect('profile')
    return view_user(request, request.user.username, todelete=item)

@login_required
def edit_gallery(request, gallery_id=None):
    item = gallery_id and get_object_or_404(Gallery, id=gallery_id, user=request.user)
    c = { 'form': GalleryForm(request.user, instance=item) }
    if request.method == 'POST':
        c['form'] = GalleryForm(request.user, request.POST, request.FILES, instance=item)
        if c['form'].is_valid():
            item = c['form'].save(commit=False)
            item.user = request.user
            item.save()
            return redirect('gallery', item.id)
    return render_to_response('resource/gallery_edit.html', c,
        context_instance=RequestContext(request))
    

@login_required
def add_to_gallery(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id, user=request.user)
    c = { 'gallery': gallery }
    if request.method == 'POST':
        c['form'] = ResourceAddForm(request.user, request.POST, request.FILES)
        if c['form'].is_valid():
            c['item'] = c['form'].save()
            # XXX We can copy over settings fromt he gallery's defaults here
            gallery.items.add(c['item'])
    return render_to_response('resource/ajax/add.txt', c,
      context_instance=RequestContext(request),
      content_type="text/plain")

    
@login_required
def paste_in(request):
    """Create a pasted text entry."""
    c = {
        'paste': True,
        'form': ResourcePasteForm(request.user),
        'breadcrumbs': breadcrumbs(request.user, "New Paste"),
    }

    if request.method == 'POST':
        c['form'] = ResourcePasteForm(request.user, request.POST)
        if c['form'].is_valid():
            return redirect('resource', c['form'].save().id)

    return render_to_response('resource/edit.html', c,
        context_instance=RequestContext(request))


@login_required
def edit_resource(request, item_id=None):
    item = item_id and get_object_or_404(Resource, id=item_id, user=request.user)
    form = FORMS.get(item and item.category and item.category.id or 0, ResourceFileForm)
    c = {
      'form': form(request.user, instance=item),
      'item': item,
      'breadcrumbs': breadcrumbs(item.user, item.gallery, item, "Edit"),
    }
    if request.method == 'POST':
        if 'cancel' in request.POST:
            if item.is_new:
                return redirect('gallery', item.gallery.id)
            return redirect('resource', item.id)
        c['form'] = form(request.user, request.POST, request.FILES, instance=item)
        if c['form'].is_valid():
            item = c['form'].save()
            if 'next' in request.POST and item.next:
                return redirect('edit_resource', item.next.id)
            return redirect(item.get_absolute_url())

    return render_to_response('resource/edit.html', c,
        context_instance=RequestContext(request))

@login_required
def create_resource(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id, user=request.user)
    c = {
      'gallery': gallery,
      'form': ResourceFileForm(request.user),
      'breadcrumbs': breadcrumbs(request.user, gallery, "Upload New Resource"),
    }
    if request.method == 'POST':
        c['form'] = ResourceFileForm(request.user, request.POST, request.FILES)
        if 'cancel' in request.POST:
            return redirect('gallery', gallery_id)
        if c['form'].is_valid():
            item = c['form'].save()
            gallery.items.add(item)
            return redirect('resource', item.id)
    return render_to_response('resource/edit.html', c,
        context_instance=RequestContext(request))


@login_required
def delete_resource(request, item_id):
    item = get_object_or_404(Resource, id=item_id, user=request.user)
    gallery = item.gallery
    if request.method == 'POST':
        if 'confirm' in request.POST:
            item.delete()
        if gallery:
            return redirect('gallery', gallery.id)
        return redirect('my_resources')

    return render_to_response('resource/delete.html', {
      'delete': True, 'item': item,
      'breadcrumbs': breadcrumbs(item.user, item.gallery, item, "Delete"),
      }, context_instance=RequestContext(request))

@login_required
def publish_resource(request, item_id):
    item = get_object_or_404(Resource, id=item_id, user=request.user)
    item.published = True
    item.save()
    return redirect("gallery", item.gallery.id)


@login_required
def view_trash(request):
    c = {
      'user': request.user,
      'items': request.user.resources.trash,
      'breadcrumbs': breadcrumbs(request.user, "Trash"),
      'gallery': {'name': _("Your Trash Space"), 'user': request.user},
      'limit': 200,
    }
    return render_to_response('resource/gallery.html', c,
             context_instance=RequestContext(request))


def view_gallery(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id)
    if not gallery.is_visible():
        raise Http404
    c = {
      'user'       : gallery.user,
      'items'      : gallery.items.for_user(request.user),
      'gallery'    : gallery,
      'breadcrumbs': breadcrumbs(gallery.user, gallery),
      'limit'      : 15 - gallery.is_editable(),
    }
    
    if gallery.group:
        c['breadcrumbs'] = breadcrumbs(gallery)

    return render_to_response('resource/gallery.html', c,
             context_instance=RequestContext(request))


def view_resource(request, item_id):
    item = get_object_or_404(Resource, id=item_id)
    if not item.is_visible():
        raise Http404

    if item.is_new:
        return redirect("edit_resource", item_id)

    item.set_viewed(request.session)
    c = {
      'item': item,
      'vote': item.votes.for_user(request.user).first(),
      'breadcrumbs': breadcrumbs(item.user, item.gallery, item),
    }
    return render_to_response('resource/view.html', c,
               context_instance=RequestContext(request))


@login_required
def like_resource(request, item_id, like_id):
    item = get_object_or_404(Resource, id=item_id)
    if item.user.pk == request.user.pk:
        raise Http404
    (like, is_new) = item.votes.get_or_create(voter=request.user)
    if like_id == '-':
        like.delete()
    return redirect("resource", item_id)
    
def down_readme(request, item_id):
    item = get_object_or_404(Resource, id=item_id)
    return render_to_response('resource/readme.txt', { 'item': item },
      context_instance=RequestContext(request),
      content_type="text/plain")


from sendfile import sendfile
from inkscape import settings

def down_resource(request, item_id, vt='d'):
    item = get_object_or_404(ResourceFile, id=item_id)

    # The view 'download' allows one to view an image in full screen glory
    # which is technically a download, but we count it as a view and try and let
    # the browser deal with showing the file.
    if vt == 'v':
        item.set_viewed(request.session)
        item.save()
        if item.mime().is_text():
            return render_to_response('resource/view_text.html', {
              'breadcrumbs': breadcrumbs(item.user, item.gallery, item, 'Full Text View'),
              'item': item,
            }, context_instance=RequestContext(request))
        return redirect(item.download.url)

    # Otherwise the user intends to download the file and we record it as such
    # before passing the download path to nginx for delivery using a content
    # despatch to force the browser into saving-as.
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
    url = item.download.path
    if not settings.DEBUG:
        # Correct for nginx redirect
        url =  '/get' + url[6:]
    return sendfile(request, url, attachment=True)


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

def view_galleries(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    # Show items which are published, OR are the same user as the requester
    filters = {}
    c = {
      'user': user,
      'me': user == request.user,
      'items': user.galleries.for_user(request.user),
      'breadcrumbs': breadcrumbs(user, "Galleries"),
      'limit'      : 15 - (user == request.user),
      # XXX 'todelete'   : todelete,
    }
    
    return render_to_response('resource/user.html', c,
        context_instance=RequestContext(request))


def mirror_resource(request, uuid, filename):
    mirror = get_object_or_404(ResourceMirror, uuid=uuid)
    item = get_object_or_404(ResourceFile, download=os.path.join('resources', 'file', filename))
    url = item.download.path
    if not settings.DEBUG:
        # Correct for nginx redirect
        url =  '/get' + url[6:]
    return sendfile(request, url, attachment=True)


from pile.views import CategoryListView, CreateView

class MirrorAdd(CreateView):
    model      = ResourceMirror
    form_class = MirrorAddForm


class GalleryList(CategoryListView):
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
        return super(GalleryList, self).base_queryset().filter(published=True)

    def get_galleries(self):
        username = self.get_value('username')
        if username:
            return User.objects.get(username=username).galleries.all()
        return Gallery.objects.none()

