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

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DeleteView, CreateView, TemplateView, View
from django.views.generic.detail import SingleObjectMixin

from pile.views import CategoryListView

from .mixins import UserRequiredMixin, OwnerRequiredMixin
from .models import User, UserAlert, Message, \
    UserAlertSetting, AlertType, AlertSubscription

class AlertList(CategoryListView, UserRequiredMixin):
    model = UserAlert
    opts = (
      ('alerttype', 'alert__slug'),
      ('new', 'viewed__isnull'),
    )

    def get_queryset(self, **kwargs):
        queryset = super(AlertList, self).get_queryset(**kwargs)
        return queryset.filter(user=self.request.user)

    def get_context_data(self, **data):
        data = super(AlertList, self).get_context_data(**data)
        if data['alerttype'] and isinstance(data['alerttype'], (tuple, list)):
            data['alerttype'] = data['alerttype'][0]
        return data


class MarkViewed(View, SingleObjectMixin, OwnerRequiredMixin):
    model = UserAlert
    function = 'view'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        getattr(obj, self.function)()
        return HttpResponse(obj.pk)
 

class MarkDeleted(MarkViewed):
    model = UserAlert
    function = 'delete'


class Subscribe(CreateView, UserRequiredMixin):
    model = AlertSubscription
    action_name = _('Subscribe')

    def get_context_data(self, **kwargs):
        data = super(Subscribe, self).get_context_data(**kwargs)
        data['alert'] = AlertType.objects.get(slug=self.kwargs['slug'])
        if 'pk' in self.kwargs:
            data['object'] = data['alert'].get_object(pk=self.kwargs['pk'])
            data['object_name'] = data['alert'].get_object_name(data['object'])
        return data

    def post(self, request, **kwargs):
        self.object = None
        data = self.get_context_data(**kwargs)
        kw = dict(user=request.user, target=self.kwargs.get('pk', None))
        (self.object, a, b) = data['alert'].subscriptions.get_or_create(**kw)
        b and messages.warning(request, _("Deleted %d previous subscription(s) (superseded)") % deleted)
        a and messages.info(request, _('Subscription created!'))
        not a and messages.warning(request, _('Already subscribed to this!'))
        return redirect('alert.settings')


class Unsubscribe(DeleteView, OwnerRequiredMixin):
    model = AlertSubscription
    action_name = _('Unsubscribe')
    get_success_url = lambda self: reverse('alert.settings')

    def get_object(self):
        if 'slug' in self.kwargs:
            alert = AlertType.objects.get(slug=self.kwargs['slug'])
            kw = dict(user=request.user)
            if 'pk' in self.kwargs:
                kw['target'] = kwargs['pk']
            else:
                kw['target__isnull'] = True
            return alert.subscriptions.get(**kw)
        return super(Unsubscribe, self).get_object()


class SettingsList(UserRequiredMixin, CategoryListView):
    model = AlertSubscription

    def get_queryset(self, **kwargs):
        return super(SettingsList, self).get_queryset(**kwargs).filter(user=self.request.user)

    def post(self, *args, **kwargs):
        data = self.request.POST
        # This proceedure is because settings are not saved unless
        # the user has changed something from the default.
        for item in UserAlertSetting.objects.get_all(self.request.user):
            changed = False
            for setting in ('email', 'hide'):
                value = bool(data.get("setting_%d_%s" % (item.alert.pk, setting), False))
                if getattr(item, setting) != value:
                    setattr(item, setting, value)
                    changed = True
            if changed:
                item.save()
        return redirect('alert.settings')

    def get_context_data(self, **data):
        data = super(SettingsList, self).get_context_data(**data)
        if not self.request.user.email:
            messages.warning(self.request,
              _("You haven't told us your mail address yet! If you would like"
              " to receive emails from inkscape.org, enter an email address"
              " <a href='%(url)s'>in your profile</a>.") % \
                {'url': reverse('edit_profile')}, extra_tags='safe')
        data['object'] = self.request.user
        data['action'] = _('Alert Settings')
        data['settings'] = UserAlertSetting.objects.get_all(self.request.user)
        return data


class SentMessages(UserRequiredMixin, ListView):
    model = Message

    def get_queryset(self):
        return self.request.user.sent_messages.all()


class CreateMessage(UserRequiredMixin, CreateView):
    model = Message
    fields = ('subject','body','recipient','reply_to')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.sender = self.request.user
        obj.reply_to = self.get_reply_to()
        obj.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('my_profile')

    def get_reply_to(self):
        msg = self.gost('reply_to', None)
        if msg:
            # If we ever want to restrict who can reply, do it here first.
            msg = get_object_or_404(self.model, pk=msg, recipient=self.request.user)
        return msg

    def get_initial(self):
        """Add reply to subject initial data"""
        initial = super(CreateMessage, self).get_initial()
        self.recipient = get_object_or_404(User, username=self.kwargs.get('username',''))
        rto = self.get_reply_to()
        if rto:
            initial['subject'] = (rto.reply_to and "Re: " or "") + rto.subject
            self.recipient = rto.sender
        initial['recipient'] = self.recipient.pk
        return initial

    def get_context_data(self, **data):
        """Add reply to message object to template output"""
        data = super(CreateMessage, self).get_context_data(**data)
        data['reply_to'] = self.get_reply_to()
        data['recipient'] = self.recipient
        return data

