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
import json

from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DeleteView, CreateView, UpdateView,\
        TemplateView, View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth import get_user_model

from .forms import MessageForm, SettingsFormSet
from .mixins import NeverCacheMixin, UserRequiredMixin, UserMixin, OwnerRequiredMixin
from .models import UserAlert, Message, UserAlertSetting, AlertType, AlertSubscription

class AlertsJson(NeverCacheMixin, UserRequiredMixin, View):
    def get(self, request):
        alerts = request.user.alerts.all()
        context = {
           'types': tuple(AlertType.objects.values()) or None,
           'new': tuple(alerts.new.values()) or None,
        }
        return JsonResponse(context)


class AlertList(NeverCacheMixin, OwnerRequiredMixin, ListView):
    """Shows a list of user alerts, user only sees their own"""
    def get_queryset(self, **kwargs):
        qs = self.request.user.alerts.all().visible
        self.breadcrumb_root = self.request.user
        if 'slug' in self.kwargs:
            self.parent = get_object_or_404(AlertType, slug=self.kwargs['slug'])
            qs = qs.filter(alert__slug=self.kwargs['slug'])
        else:
            self.parent = (reverse('alerts'), _('Alerts'))

        if 'new' in self.request.GET:
            self.title = _("New")
            qs = qs.filter(viewed__isnull=True, deleted__isnull=True)
        return qs.order_by('viewed', '-created')

    def get_context_data(self, **data):
        data = super(AlertList, self).get_context_data(**data)
        # Disable alert vew
        data['alerts'] = True
        return data




class MarkViewed(NeverCacheMixin, OwnerRequiredMixin, View, SingleObjectMixin):
    model = UserAlert
    function = 'view'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        getattr(obj, self.function)()
        return HttpResponse(json.dumps({self.function: [obj.pk]}))


class MarkAllViewed(AlertList):
    function = 'view'

    def get(self, request, *args, **kwargs):
        objs = self.get_queryset()
        # This list() MUST happen before the function otherwise delete
        # will return an empty list and fail to update the html.
        pks = list(objs.values_list('pk', flat=True))

        getattr(objs, self.function + '_all')()
        return HttpResponse(json.dumps({self.function: list(pks)}))
 

class MarkDeleted(MarkViewed):
    function = 'delete'

class MarkAllDeleted(MarkAllViewed):
    function = 'delete'


class Subscribe(NeverCacheMixin, UserRequiredMixin, CreateView):
    model = AlertSubscription
    fields = [] # Everything is in url or context

    def get_context_data(self, **kwargs):
        data = super(Subscribe, self).get_context_data(**kwargs)
        self.breadcrumb_root = self.request.user
        data['alert'] = get_object_or_404(AlertType, slug=self.kwargs['slug'])
        data['object'] = data['alert']
        if 'pk' in self.kwargs:
            try:
                subscription = data['alert'].get_object(pk=self.kwargs['pk'])
            except data['alert'].sender.DoesNotExist:
                raise Http404("Alert subscription doesn't exist")

            data['object_name'] = data['alert'].get_object_name(subscription)
            data['title'] = _('Subscribe to %(object_name)s') % data
        else:
            data['alert_name'] = data['alert'].name
            data['title'] = _('Subscribe to All %(alert_name)s') % data
        return data

    def post(self, request, **kwargs):
        self.object = None
        data = self.get_context_data(**kwargs)
        kw = dict(user=request.user, target=self.kwargs.get('pk', None))
        (self.object, a, b) = data['alert'].subscriptions.get_or_create(**kw)
        b and messages.warning(request, _("Deleted %d previous subscription(s) (superseded)") % b)
        a and messages.info(request, _('Subscription created!'))
        not a and messages.warning(request, _('Already subscribed to this!'))
        return redirect('alert.settings')


class Unsubscribe(NeverCacheMixin, OwnerRequiredMixin, DeleteView):
    model = AlertSubscription
    get_success_url = lambda self: reverse('alert.settings')

    def get_context_data(self, **kwargs):
        data = super(Unsubscribe, self).get_context_data(**kwargs)
        self.breadcrumb_root = self.request.user
        data['alert'] = AlertType.objects.get(slug=self.kwargs['slug'])
        data['object'] = data['alert']
        data['delete'] = True
        if 'pk' in self.kwargs:
            subscription = data['alert'].get_object(pk=self.kwargs['pk'])
            data['object_name'] = data['alert'].get_object_name(subscription)
            data['title'] = _('Unsubscribe from %(object_name)s') % data
        else:
            data['alert_name'] = data['alert'].name
            data['title'] = _('Unsubscribe from All')
        return data
    
    def get_object(self):
        if 'slug' in self.kwargs:
            alert = get_object_or_404(AlertType, slug=self.kwargs['slug'])
            kw = dict(user=self.request.user)
            if 'pk' in self.kwargs:
                kw['target'] = self.kwargs['pk']
            else:
                kw['target__isnull'] = True
            return get_object_or_404(alert.subscriptions, **kw)
        return super(Unsubscribe, self).get_object()


class SettingsList(NeverCacheMixin, UserMixin, UpdateView):
    title = _('Your Alert Settings')
    form_class = SettingsFormSet
    template_name = 'alerts/alertsettings.html'

    def get_context_data(self, **data):
        data = super(SettingsList, self).get_context_data(**data)
        data['formset'] = data.pop('form')
        return data

    def get_success_url(self):
        return reverse('alert.settings')


class SentMessages(NeverCacheMixin, UserRequiredMixin, ListView):
    model = Message
    title = _('Outbox')

    def get_queryset(self):
        return self.request.user.sent_messages.all()

    def get_parent(self):
        return self.request.user


class CreateMessage(NeverCacheMixin, UserRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.sender = self.request.user
        obj.save()
        messages.info(self.request, _('Message Sent to %s') % unicode(obj.recipient))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('my_profile')

    def get_reply_to(self):
        if 'pk' in self.kwargs:
            # If we ever want to restrict who can reply, do it here first.
            return get_object_or_404(self.model, pk=self.kwargs['pk'], recipient=self.request.user)

    def get_initial(self):
        """Add reply to subject initial data"""
        initial = super(CreateMessage, self).get_initial()
        self.recipient = get_object_or_404(get_user_model(), username=self.kwargs.get('username',''))
        rto = self.get_reply_to()
        if rto:
            initial['subject'] = rto.subject
            if not rto.reply_to:
                initial['subject'] = "Re: " + initial['subject']
        if 'pk' in self.kwargs:
            initial['reply_to'] = self.kwargs['pk']
        initial['recipient'] = self.recipient.pk
        return initial

    def get_context_data(self, **data):
        """Add reply to message object to template output"""
        data = super(CreateMessage, self).get_context_data(**data)
        data['reply_to'] = self.get_reply_to()
        data['recipient'] = self.recipient
        data['object_list'] = Message.objects.all()
        data['object_list'].parent = self.recipient

        data['title'] = _("Send New Message")
        if data['reply_to']:
            data['title'] = _("Send Reply Message")

        return data

