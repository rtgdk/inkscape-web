# -*- coding: utf-8 -*-
#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
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
Views for resource system, adding items, entering new categories for widgets etc
"""

import sys
import os

from sendfile import sendfile
from datetime import timedelta

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.conf import settings
from django.template import RequestContext

from person.models import User
from pile.views import *

from .mixins import *
from .models import *
from .forms import *

class GalleryMixin(object):
    pk_url_kwarg = 'gallery_id'
    model = Gallery


class DeleteGallery(GalleryMixin, OwnerDeleteMixin, DeleteView):
    title = _("Delete Gallery")

class CreateGallery(GalleryMixin, OwnerCreateMixin, CreateView):
    form_class = GalleryForm
    title = _("Create Gallery")

class EditGallery(GalleryMixin, OwnerUpdateMixin, UpdateView):
    title = _("Edit Gallery")
    form_class = GalleryForm
    get_group = lambda self: None

class GalleryList(GalleryMixin, OwnerViewMixin, ListView):
    pass

class DeleteResource(OwnerDeleteMixin, DeleteView):
    model = Resource
    title = _("Delete")

class EditResource(OwnerUpdateMixin, UpdateView):
    model = Resource
    title = _("Edit")

    def get_form_class(self):
        category = getattr(self.object.category, 'id', 0)
        return FORMS.get(category, ResourceForm)

    def get_form_kwargs(self):
        kw = super(EditResource, self).get_form_kwargs()
        if self.object.gallery:
            kw['gallery'] = self.object.gallery
        return kw

class PublishResource(OwnerUpdateMixin, DetailView):
    model = Resource
    title = _("Publish")

    def post(self, request, *args, **kwargs):
        item = self.get_object()
        item.published = True
        item.save()
        return redirect(item.get_absolute_url())


class MoveResource(OwnerUpdateMixin, UpdateView):
    template_name = 'resources/resource_move.html'
    form_class = GalleryMoveForm
    model = Resource
    
    def get_object(self):
        self.source = None
        self.title = _('Copy to Gallery')
        if 'source' in self.kwargs:
            self.title = _('Move to Gallery')
            self.source = get_object_or_404(Gallery, pk=self.kwargs['source'])
        return super(MoveResource, self).get_object()

    def get_group(self):
        """This gives group members permisson to move other's resources"""
        return getattr(self.source, 'group', None)

    def get_form_kwargs(self):
        kwargs = super(MoveResource, self).get_form_kwargs()
        kwargs['source'] = self.source
        return kwargs

    def form_invalid(self, form):
        for error in form.errors.as_data().get('target', []):
            if error.code == 'invalid_choice':
                raise PermissionDenied()
        return super(MoveResource, self).form_invalid(form)

    def get_success_url(self):
        return self.get_object().get_absolute_url()


class UploadResource(OwnerCreateMixin, CreateView):
    form_class = ResourceForm
    model = Resource
    title = _("Upload New Resource")

    def get_form_kwargs(self):
        kw = super(UploadResource, self).get_form_kwargs()
        if hasattr(self, 'gallery'):
            kw['gallery'] = self.gallery
        return kw


class DropResource(UploadResource):
    content_type  = 'text/plain'
    template_name = 'resources/ajax/add.txt'
    form_class    = ResourceAddForm

    def form_valid(self, form):
        ret = super(DropResource, self).form_valid(form)
        context = self.get_context_data(item=form.instance)
        return self.render_to_response(context)


class PasteIn(UploadResource):
    form_class = ResourcePasteForm
    title = _("New PasteBin")

    def get_context_data(self, **kw):
        data = super(PasteIn, self).get_context_data(**kw)
        data['object'] = Category.objects.get(pk=1)
        data['object'].parent = self.request.user.resources.all()
	data['object_list'] = None
	return data


class ViewResource(DetailView):
    model = Resource
    
    def get_queryset(self):
        qs = Resource.objects.for_user(self.request.user)
        if 'username' in self.kwargs:
            return qs.filter(user__username=self.kwargs['username'])
        return qs

    def get_template_names(self, *args, **kw):
        if self.request.GET.get('modal', False):
            return 'resources/resource_modal.html'
        return super(ViewResource, self).get_template_names(*args, **kw)

    def get(self, request, *args, **kwargs):
        ret = super(ViewResource, self).get(request, *args, **kwargs)
        if self.object.is_new:
            return redirect("edit_resource", self.object.pk)
        if request.user != self.object.user:
            if self.object.set_viewed(request.session) is None:
                request.session['test'] = 'True'
                self.object.set_viewed(request.session)
        return ret


class TagsJson(View):
    def get(self, request):
        # We could leverage category to style
        # categorized tags differently in the suggestions list
        context = {"tags" : [{"name": tag.name, "cat" : str(tag.category)} for tag in Tag.objects.all()]}
        return JsonResponse(context, safe=False, content_type='application/json; charset=utf-8')


@login_required
def like_resource(request, pk, like):
    item = get_object_or_404(Resource, pk=pk, published=True)
    if item.user.pk == request.user.pk:
        raise PermissionDenied()

#    if item.category.start_contest:
#        # Some different rules for contest categories
#        if item.category.start_contest > now().date():
#            messages.warning(request, _('You may not vote until the contest begins.'))
#            return redirect(item.get_absolute_url())
#        if item.category.end_contest and item.category.end_contest < now().date():
#            messages.warning(request, _('You may not vote after the contest ends.'))
#            return redirect(item.get_absolute_url())
#        votes = item.category.votes.filter(voter=request.user)
#        if votes.count() > 0 and '+' in like:
#            for vote in votes:
#                vote.delete()
#            if votes.filter(resource_id=item.id).count() == 0:
#                messages.info(request, _('Your previous vote in this contest has been replaced by your vote for this item.'))

    (obj, is_new) = item.votes.get_or_create(voter=request.user)
    if '+' not in like:
        obj.delete()
    #elif is_new == True and item.category.start_contest:
    #    messages.info(request, _('Thank you for your vote!'))
    return redirect(item.get_absolute_url())
    
def down_readme(request, pk):
    item = get_object_or_404(Resource, id=pk)
    return render_to_response('resources/readme.txt', {'item': item},
      context_instance=RequestContext(request),
      content_type="text/plain")


class DownloadResource(ViewResource):
    template_name = 'resources/view_text.html'

    def get(self, request, *args, **kwargs):
        fn = kwargs.get('fn', None)
        item = self.get_object()
        if not item.download:
            messages.warning(request, _('There is no file to download in this resource.'))
            return redirect(item.get_absolute_url())

        # The view 'download' allows one to view an image in full screen glory
        # which is technically a download, but we count it as a view and try
        # and let the browser deal with showing the file.
        if fn is None:
            if item.mime().is_text():
                return super(DownloadResource, self).get(request, *args, **kwargs)
            item.fullview += 1
            item.save()
            return redirect(item.download.url)

        if fn not in ['download', item.filename()]:
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
                response = render_to_response('resources/resourcemirror_thanks.html', {
                     'mirror': mirror,
                     'item': item,
                     'url': mirror.get_url(item),
                   }, context_instance=RequestContext(request))
                response['refresh'] = "3; url=%s" % mirror.get_url(item)
                return response

        if settings.DEBUG:
            # We still use sendfile for development because it's useful
            return sendfile(request, item.download.path, attachment=True)

        # But live now uses nginx directly to set the Content-Disposition
        # since the header will be passed to the fastly cache from nginx
        # but the sendfile method will fail because of the internal redirect.
        return redirect(item.download.url.replace('/media/', '/dl/'))


class MirrorIndex(ListView):
    model = ResourceMirror

class MirrorView(DetailView):
    model = ResourceMirror
    slug_field = 'uuid'

    def get(self, *args, **kw):
        self.get_object().do_sync()
        return super(MirrorView, self).get(*args, **kw)

class MirrorResource(MirrorView):
    def get(self, request, *args, **kw):
        mirror = self.get_object()
        path = os.path.join('resources', 'file', self.kwargs['filename'])
        url = get_object_or_404(Resource, download=path).download.path
        if not settings.DEBUG:
            # use nginx context-disposition on live
            return redirect(url.replace('/media/', '/dl/'))
        # Still use sendfile for local development
        return sendfile(request, url, attachment=True)

class MirrorAdd(CreateView):
    model = ResourceMirror
    form_class = MirrorAddForm

    def get_context_data(self, **kw):
        data = super(MirrorAdd, self).get_context_data(**kw)
        data['object_list'] = ResourceMirror.objects.all()
        data['title'] = _("Create")
        return data


class ResourceList(CategoryListView):
    rss_view = 'resources_rss'
    model = Resource
    opts = (
      ('username', 'user__username'),
      ('team', 'galleries__group__team__slug', False),
      ('gallery_id', 'galleries__id', False),
      ('tags', 'tags__name', False),
    )
    cats = (
      #('media_type', _("Media Type")),
      ('category', _("Media Category"), 'get_categories'),
      ('license', _("License"), 'get_licenses'),
      ('galleries', _("Galleries"), 'get_galleries'),
    )
    order = '-liked'
    orders = (
      ('-liked', _('Most Popular')),
      ('-viewed', _('Most Views')),
      ('-downed', _('Most Downloaded')),
      ('-edited', _('Last Updated')),
    )

    def get_template_names(self):
        if self.get_value('category'):
            return ['resources/resourcegallery_specific.html']
        return ['resources/resourcegallery_general.html']

    def extra_filters(self):
        if self.get_value('username') != self.request.user.username:
            return dict(published=True)
        return {}

    def get_licenses(self):
        return License.objects.filter(filterable=True)

    def get_categories(self):
        return Category.objects.all()

    def get_galleries(self):
        username = self.get_value('username')
        if username:
            try:
                return User.objects.get(username=username)\
                    .galleries.filter(group__isnull=True)
            except User.DoesNotExist:
                return None
        team = self.get_value('team')
        if team:
            return Group.objects.get(team__slug=team).galleries.all()
        category = self.get_value('category')
        if category:
            from .models import slugify
            for c in self.get_categories():
                if slugify(c.name) == category:
                    return Gallery.objects.filter(category_id=c.pk)
        return None

    def get_context_data(self, **kwargs):
        data = super(ResourceList, self).get_context_data(**kwargs)

        if 'team' in data and data['team']:
            # Our options are not yet returning the correct item
            data['team'] = Group.objects.get(team__slug=data['team'])
            data['team_member'] = self.request.user in data['team'].user_set.all()
            data['object_list'].instance = data['team']
        elif data['username']:
            data['object_list'].instance = data['username']
        
        if 'galleries' in data and data['galleries']:
            # our options are not yet returning the correct item
            try:
                data['galleries'] = Gallery.objects.get(slug=data['galleries'])
                data['object'] = data['galleries']
            except Gallery.DoesNotExist:
                data['galleries'] = None

        if 'category' in data:
            data['tag_categories'] = data['category'].tags.all()
            if 'galleries' not in data or not getattr(data['galleries'], 'category'):
                if 'object' in data:
                    # Set parent manually, since categories don't naturally have parents.
                    data['category'].parent = data['object']
                data['object'] = data['category']

            # Remove media type side bar if category isn't filterable.
            if not data['category'].filterable:
                for cat in data['categories']:
                    if cat is not None and cat.cid == 'category':
                        cat[:] = [cat.value]

        if 'tags' in data:
            data['tag_clear_url'] = self.get_url(exclude='tags')

        if data['username'] == self.request.user \
          or ('galleries' in data and data.get('team_member', False)):
            k = {}
            if data.get('galleries', None) is not None:
                k['gallery_id'] = data['galleries'].pk
            data['upload_url'] = reverse("resource.upload", kwargs=k)
            data['upload_drop'] = reverse("resource.drop", kwargs=k)

        return data


class GalleryView(ResourceList):
    """Allow for a special version of the resource display for galleries"""
    opts = ResourceList.opts + \
       (('galleries', 'galleries__slug', False),)
    cats = (('category', _("Media Category"), 'get_categories'),)

    def get_template_names(self):
        return ['resources/resourcegallery_specific.html']


class ResourcePick(ResourceList):
    def get_template_names(self):
        return ['resources/resource_picker.html']

class ResourceFeed(CategoryFeed, ResourceList):
    title = _("Gallery Feed")
    description = "Gallery Resources RSS Feed"

    def extra_filters(self):
        # Limit RSS feeds to the last month
        extra = super(ResourceFeed, self).extra_filters()
        extra['created__gt'] = now() - timedelta(days=32)
        return extra

    def items(self):
        for item in CategoryFeed.items(self):
            if self.query:
                yield item.object
            else:
                yield item

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description

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

