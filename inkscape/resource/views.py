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
from .forms import FORMS, ResourceFileForm, GalleryForm, ResourceAddForm

from cStringIO import StringIO

def breadcrumbs(*args):
    yield ('/', _('Home'))
    for model in args:
        if type(model) is str:
            yield ("", _(model))
        elif model is None:
            pass
        elif not hasattr(model, "get_absolute_url"):
            raise ValueError("Refusing the make '%s' into a breadcrumb!" % str(model))
        else:
            yield (model.get_absolute_url(), str(model))

@login_required
def delete_gallery(request, item_id):
    item = get_object_or_404(Gallery, id=item_id, user=request.user)
    if request.method == 'POST':
        if 'confirm' in request.POST:
            item.delete()
        return redirect('my_resources')
    return view_user(request, request.user.id, todelete=item)

@login_required
def edit_gallery(request, item_id=None):
    item = item_id and get_object_or_404(Gallery, id=item_id, user=request.user)
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
    if request.method == 'POST':
        cat = Category.objects.get(pk=1)
        count = ResourceFile.objects.filter(user=request.user, category=cat).count()

        # This knowingly ignores the quota (delibrate)
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
    return redirect('my_resources')

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
def my_resources(request):
    return view_user(request, request.user.id)


def view_list(request, **kwargs):
    c = {}
    items = Resource.objects.all()
    if request.GET.get('pub', None) != 'All':
        items = items.filter(published=True)
    for i in ('category','user'):
        if kwargs.has_key(i+'_id'):
            t = globals()[i.title()].objects.get(pk=kwargs[i+'_id'])
            items = items.filter(**{i:t})
            c['o_'+i] = t
    c['breadcrumbs'] = breadcrumbs(*c.values())
    c['items'] = items
    # I hate this hack, name should be available in the template, but it's not!
    c['name'] = c.has_key('o_user') and c['o_user'].name()
    c['limit'] = 15
    return render_to_response('resource/category.html', c,
             context_instance=RequestContext(request))


def gallery_icon(request, gallery_id):
    """This attempted to make exciting dynamic icons but doesn't work with Firefox"""
    gallery = get_object_or_404(Gallery, id=gallery_id)
    c = dict(image=gallery.items.all().order_by('created')[:3])
    return render_to_response('resource/preview/three.svg', c,
      context_instance=RequestContext(request),
      content_type="image/svg+xml")

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
    if not gallery.is_visible(request.user):
        raise Http404
    c = {
      'user'       : gallery.user,
      'items'      : gallery.items.for_user(request.user),
      'gallery'    : gallery,
      'breadcrumbs': breadcrumbs(gallery.user, gallery),
      'limit'      : 15,
    }
    if gallery.group:
        c['breadcrumbs'] = breadcrumbs(gallery)

    return render_to_response('resource/gallery.html', c,
             context_instance=RequestContext(request))


def view_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # Show items which are published, OR are the same user as the requester
    filters = {}
    c = {
      'user': user,
      'me': user == request.user,
      'items': user.galleries.for_user(request.user),
      'breadcrumbs': breadcrumbs(user, "Galleries"),
      'limit': 15,
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


@login_required
def like_resource(request, item_id, like_id):
    item = get_object_or_404(Resource, id=item_id)
    (like, is_new) = item.votes.get_or_create(voter=request.user)
    if not is_new and like_id == '-':
        like.delete()
    elif like_id == '+':
        like.vote = True
        like.save()
    return redirect("resource", item_id)
    

def down_resource(request, item_id):
    item = get_object_or_404(Resource, id=item_id)
    item.downed += 1
    item.save()
    return redirect(item.download.url)

