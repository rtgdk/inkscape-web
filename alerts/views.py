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

from pile.views import ListView, CreateView, CategoryListView
from .models import User, UserAlert, Message, UserAlertSetting, AlertSubscription
from .signals import SIGNALS

class AlertList(CategoryListView):
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


@login_required
def mark_viewed(request, alert_id):
    alert = get_object_or_404(UserAlert, pk=alert_id, user=request.user)
    alert.view()
    return HttpResponse(alert.pk)


@login_required
def mark_deleted(request, alert_id):
    alert = get_object_or_404(UserAlert, pk=alert_id, user=request.user)
    alert.delete()
    return HttpResponse(alert.pk)

@login_required
def subscribe(request, slug, pk=None):
    (alert, alerter) = SIGNALS.get(slug, (None, None))
    if not alerter or alerter.private:
        raise Http404()

    # XXX This logic needs to move into models
    model = alerter.sender
    if alerter.target:
        # Always must be a foreignKey field!
        model = getattr(model, alerter.target).field.rel.to

    obj = pk and get_object_or_404(model, pk=pk)

    if request.method == 'POST':
        (item, created, deleted) = AlertSubscription.objects.get_or_create(
                                     alert=alert, user=request.user, target=pk)
        if deleted:
            messages.warning(request, _("Deleted %d previous subscriptions (supseeded)") % deleted)
        if created:
            messages.info(request, _('Subscription created!'))
        else:
            messages.warning(request, _('Already subscribed to this!'))
        return redirect('alert.settings')

    return render_to_response('alerts/subscribe.html', {
        'alert': alert,
        'object': obj,
      }, context_instance=RequestContext(request))

@login_required
def unsubscribe(request, pk):
    sub = get_object_or_404(AlertSubscription, pk=pk, user=request.user)
    sub.delete()
    return redirect('alert.settings')


class SettingsList(CategoryListView):
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
        data['settings'] = UserAlertSetting.objects.get_all(self.request.user)
        return data


class SentMessages(ListView):
    model = Message

    def get_queryset(self):
        return self.request.user.sent_messages.all()


class CreateMessage(CreateView):
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

