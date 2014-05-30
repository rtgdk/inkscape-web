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

from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Q

from django.contrib.auth.models import User

from .models import Resource, Category, License, Gallery
from .forms import ResourceFileForm, GalleryForm

def breadcrumbs(*args):
    yield ('/', _('Home'))
    for model in args:
        yield (model.get_absolute_url(), str(model))

@login_required
def delete_gallery(request, item_id):
    item = get_object_or_404(Gallery, id=item_id)
    if item.user != request.user:
        raise Http404
    if request.method == 'POST':
        if 'confirm' in request.POST:
            item.delete()
        return redirect('my_resources')
    return view_user(request, request.user.id, item)

@login_required
def edit_gallery(request, item_id=None):
    item = item_id and get_object_or_404(Gallery, id=item_id)
    c = { 'form': GalleryForm(instance=item) }
    if request.method == 'POST':
        c['form'] = GalleryForm(request.POST, request.FILES, instance=item)
        if c['form'].is_valid():
            item = c['form'].save(commit=False)
            item.user = request.user
            item.save()
    return redirect('my_resources')

@login_required
def add_to_gallery(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id, user=request.user)
    c = { 'gallery': gallery }
    if request.method == 'POST':
        form = ResourceFileForm(request.POST, request.FILES)
        if form.is_valid():
            c['item']= form.save(commit=False)
            c['item'].user = request.user
            c['item'].save()
            if not c['item'].download:
                raise ValueError("File wasn't saved, WTF.")
            # XXX We can copy over settings fromt he gallery's defaults here
            gallery.items.add(c['item'])
        c['form'] = form 
    return render_to_response('resource/ajax/add.txt', c,
      context_instance=RequestContext(request),
      content_type="text/plain")
    

@login_required
def edit_resource(request, item_id=None):
    item = item_id and get_object_or_404(Resource, id=item_id)
    c = { 'form': ResourceFileForm(instance=item) }
    if request.method == 'POST':
        c['form'] = ResourceFileForm(request.POST, request.FILES, instance=item)
        if c['form'].is_valid():
            item = c['form'].save(commit=False)
            item.user = request.user
            item.save()
            return redirect('resource', item.id)

    return render_to_response('resource/edit.html', c,
        context_instance=RequestContext(request))

@login_required
def delete_resource(request, item_id, confirm='n'):
    item = get_object_or_404(Resource, id=item_id)
    if item.user != request.user:
        raise Http404
    if confirm != 'y':
        return render_to_response('resource/confirm.html', { 'item': item },
            context_instance=RequestContext(request))
    item.delete()
    return redirect('my_resources')

@login_required
def my_resources(request):
    return view_user(request, request.user.id)


def view_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    # We never show unpublished items, even to their owners
    c = {
        'items': Resource.objects.filter(category=category, published=True),
        'category': category,
        'breadcrumbs': breadcrumbs(category),
    }
    return render_to_response('resource/category.html', c,
             context_instance=RequestContext(request))


def gallery_icon(request, gallery_id):
    """This attempted to make exciting dynamic icons but doesn't work with Firefox"""
    gallery = get_object_or_404(Gallery, id=gallery_id)
    c = dict(image=gallery.items.all().order_by('created')[:3])
    return render_to_response('resource/preview/three.svg', c,
      context_instance=RequestContext(request),
      content_type="image/svg+xml")


def view_gallery(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id)
    if not gallery.is_visible(request.user):
        raise Http404
    c = {
        'user'       : gallery.user,
        'items'      : gallery.items.for_user(request.id),
        'gallery'    : gallery,
        'breadcrumbs': breadcrumbs(gallery.user, gallery),
    }
    return render_to_response('resource/gallery.html', c,
             context_instance=RequestContext(request))


def view_user(request, user_id, todelete=None):
    user = get_object_or_404(User, id=user_id)
    # Show items which are published, OR are the same user as the requester
    c = {
        'user': user,
        'items': user.galleries.for_user(request.user),
        'todelete': todelete,
        'breadcrumbs': breadcrumbs(user),
    }
    return render_to_response('resource/user.html', c,
        context_instance=RequestContext(request))


def view_resource(request, item_id):
    item = get_object_or_404(Resource, id=item_id)
    if not item.is_visible(request.user):
        raise Http404

    return render_to_response('resource/item.html', {
      'item': item,
      'breadcrumbs': breadcrumbs(item.user, item.gallery, item),
    }, context_instance=RequestContext(request))

