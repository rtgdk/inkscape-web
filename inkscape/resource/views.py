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
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.utils.timezone import now
from django.contrib.auth.models import User

from .models import Resource, ResourceFile, Category, License, Gallery
from .forms import ResourceFileForm, GalleryForm, ResourceAddForm

from cStringIO import StringIO

def breadcrumbs(*args):
    yield ('/', _('Home'))
    for model in args:
        if type(model) is str:
            yield ("", model)
        elif model is None:
            pass
        else:
            yield (model.get_absolute_url(), str(model))

@login_required
def delete_gallery(request, item_id):
    item = get_object_or_404(Gallery, id=item_id, user=request.user)
    if request.method == 'POST':
        if 'confirm' in request.POST:
            item.delete()
        return redirect('my_resources')
    return view_user(request, request.user.id, item)

@login_required
def edit_gallery(request, item_id=None):
    item = item_id and get_object_or_404(Gallery, id=item_id, user=request.user)
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
        form = ResourceAddForm(request.POST, request.FILES)
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
def paste_in(request):
    """Create a pasted text entry."""
    if request.method == 'POST':
        cat = Category.objects.get(pk=1)
        count = ResourceFile.objects.filter(user=request.user, category=cat).count()

        res = ResourceFile(
          license=License.objects.get(pk=1), category=cat,
          name=_("Pasted Text #%d") % count, user=request.user,
          desc="-", owner=True, published=True,
        )
        
        filename = "pasted-%s-%d.txt" % (request.user.username, count)
        buf = StringIO(request.POST['text'])
        buf.seek(0, 2)
        fil = InMemoryUploadedFile(buf, "text", filename, None, buf.tell(), None)
        res.download.save(fil.name, fil) # Does res.save()

        return redirect('edit_resource', res.id)
    return redirect('home')

@login_required
def edit_resource(request, item_id=None):
    item = item_id and get_object_or_404(Resource, id=item_id, user=request.user)
    c = {
      'form': ResourceFileForm(instance=item),
      'item': item,
    }
    if request.method == 'POST':
        if 'cancel' in request.POST:
            if item.is_new:
                return redirect('gallery', item.gallery.id)
            return redirect('resource', item.id)
        c['form'] = ResourceFileForm(request.POST, request.FILES, instance=item)
        if c['form'].is_valid():
            item = c['form'].save(commit=False)
            if not item.user:
                item.user = request.user
            item.save()
            if 'next' in request.POST and item.next:
                return redirect('edit_resource', item.next.id)
            if item.category and item.category.id == 1:
                return redirect('pasted_item', item.id)
            return redirect('resource', item.id)

    return render_to_response('resource/edit.html', c,
        context_instance=RequestContext(request))

@login_required
def create_resource(request, gallery_id):
    gallery = get_object_or_404(Gallery, id=gallery_id, user=request.user)
    c = {
      'gallery': gallery,
      'form': ResourceFileForm(),
    }
    if request.method == 'POST':
        c['form'] = ResourceFileForm(request.POST, request.FILES)
        if c['form'].is_valid():
            item = c['form'].save(commit=False)
            item.user = request.user
            item.save()
            gallery.items.add(item)
            return redirect('resource', item.id)
    return render_to_response('resource/create.html', c,
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

    return render_to_response('resource/delete.html', { 'delete': True, 'item': item },
            context_instance=RequestContext(request))

@login_required
def publish_resource(request, item_id):
    item = get_object_or_404(Resource, id=item_id, user=request.user)
    item.published = True
    item.save()
    return redirect("gallery", item.gallery.id)

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
        'items'      : gallery.items.for_user(request.user),
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
        'breadcrumbs': breadcrumbs(user, "Galleries"),
    }
    return render_to_response('resource/user.html', c,
        context_instance=RequestContext(request))


def view_resource(request, item_id):
    item = get_object_or_404(Resource, id=item_id)
    if not item.is_visible(request.user):
        raise Http404

    if item.is_new:
        return redirect("edit_resource", item_id)

    item.viewed += 1
    item.save()
    vote = item.votes.for_user(request.user)
    if not len(vote):
        vote = (None,)

    return render_to_response('resource/view.html', {
      'item': item,
      'vote': vote[0],
      'breadcrumbs': breadcrumbs(item.user, item.gallery, item),
    }, context_instance=RequestContext(request))

def like_resource(request, item_id, like_id="+"):
    item = get_object_or_404(Resource, id=item_id)
    like = item.votes.get_or_create(voter=request.user)[0]
    like.vote = like_id == "+"
    like.save()
    return redirect("resource", item_id)
    

def down_resource(request, item_id):
    item = get_object_or_404(Resource, id=item_id)
    item.downed += 1
    item.save()
    return redirect(item.download.url)

