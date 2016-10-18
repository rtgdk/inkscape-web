#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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
Forums are a simple extension of django_comments and there really
shouldn't be much functionality contained within this app.
"""

import json

from collections import OrderedDict

from django.db.models import *
from django.template.loader import get_template
from django.template.base import TemplateDoesNotExist

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator

from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.text import slugify
from django_comments.models import Comment

from django.apps import apps
app = apps.get_app_config('forums')

class SelectRelatedQuerySet(QuerySet):
    """Automatically select related ForeignKeys to queryset"""
    def __init__(self, *args, **kw):
        super(SelectRelatedQuerySet, self).__init__(*args, **kw)
        self.query.select_related = True

    def groups(self):
        ret = OrderedDict()
        for item in self:
            if item.group.name not in ret:
                ret[item.group.name] = []
            ret[item.group.name].append(item)
        return ret


@python_2_unicode_compatible
class ForumGroup(Model):
    name = CharField(max_length=128, unique=True)

    breadcrumb_name = lambda self: self.forums.all().breadcrumb_name()
    get_absolute_url = lambda self: self.forums.all().get_absolute_url()
    parent = property(lambda self: self.forums.all().parent)

    def __str__(self):
        return self.name

class ForumQuerySet(SelectRelatedQuerySet):
    @property
    def parent(self):
        page = reverse('pages-details-by-slug', kwargs={'slug': 'community'})
        return (page, _('Community'))

    def breadcrumb_name(self):
        return _('Forums')

    def get_absolute_url(self):
        return reverse('forums:list')


@python_2_unicode_compatible
class Forum(Model):
    group = ForeignKey(ForumGroup, related_name='forums')
    sort = IntegerField(default=0, null=True, blank=True)

    name = CharField(max_length=128, unique=True)
    slug = SlugField(max_length=128, unique=True)
    desc = TextField(validators=[MaxLengthValidator(1024)], null=True, blank=True)
    icon = FileField(upload_to='forum/icon', null=True, blank=True)

    lang = CharField(max_length=8, null=True, blank=True,
            help_text=_('Set this ONLY if you want this forum restricted to this language'))

    content_type = ForeignKey(ContentType, null=True, blank=True,
            verbose_name=_('Fixed Content From'), help_text="When fixed conte"
            "nt is set, new topics can not be created. Instead, commented ite"
            "ms are automatically posted as topics.")
    sync = CharField(max_length=64, null=True, blank=True, choices=app.sync_choices,
            verbose_name=_('Sync From'), help_text="When sync source is "
            "set, new topics and messages can not be created. Instead, sync m"
            "essages are collated into topics and replies by helper scripts")

    last_posted = DateTimeField(_('Last Posted'), db_index=True, null=True, blank=True)

    objects = ForumQuerySet.as_manager()

    class Meta:
        get_latest_by = 'last_posted'
        ordering = ('-sort',)

    def __str__(self):
        return self.name

    @property
    def parent(self):
        return self.group

    def model_class(self):
        return self.content_type.model_class()

    def get_absolute_url(self):
        return reverse('forums:detail', kwargs={'slug': self.slug})

    def save(self, **kw):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Forum, self).save(**kw)

    @property
    def sync_config(self):
        return settings.FORUM_SYNCS.get(self.sync, {})

    def sync_message(self, message):
        """Add a new message xor forum topic based on an import"""
        if not message:
            return
        objects = CommentLink.objects
        message_id = message.get_message_id()
        reply_id = message.get_reply_id()

        links = objects.filter(message_id=message_id)
        if links.count() == 1:
            return links.get().comment

        reply_to = objects.filter(message_id=reply_id)
        if reply_to.count() > 0:
            topic = reply_to.get().comment.content_object
            created = None
        else:
            topic, created = self.topics.get_or_create(
              message_id=message_id,
              defaults={
                'subject': unicode(message.get_subject()),
              }
            )

        if created in (None, True):
            comment = Comment.objects.create(
                site_id=1,
                user=message.get_user(),
                user_name=unicode(message.get_username()),
                user_email=message.get_email(),
                user_url=message.get_userurl(),
                comment=unicode(message.get_body()),
                submit_date=message.get_created(),
                content_object=topic,
            )

            link = objects.create(
                comment=comment,
                message_id=message_id,
                reply_id=reply_id,
                subject=message.get_subject(),
                extra_data=json.dumps(message.get_data()),
            )

        if created and hasattr(message, 'get_replies'):
            for reply in message.get_replies():
                comment = Comment.objects.create(
                    site_id=1,
                    user=message.get_user(),
                    user_name=unicode(message.get_username()),
                    user_email=message.get_email(),
                    user_url='',
                    comment=unicode(reply.get_body()),
                    submit_date=message.get_created(),
                    content_object=topic,
                )

        return comment


class ForumTopic(Model):
    """When a forum allows free standing topics (without connection to an object)"""
    forum = ForeignKey(Forum, related_name='topics')
    object_pk = PositiveIntegerField(null=True, blank=True)
    subject = CharField(max_length=128)
    slug = SlugField(max_length=128, unique=True)

    message_id = CharField(max_length=255, db_index=True, null=True, blank=True)

    last_posted = DateTimeField(_('Last Posted'), db_index=True, null=True, blank=True)
    sticky = IntegerField(_('Sticky Priority'), default=0,
        help_text=_('If set, will stick this post to the top of the topics '
          'list. Higher numbers appear nearer the top. Same numbers will '
          'appear together, sorted by date.'))
    locked = BooleanField(default=False, help_text=_('Topic is locked by moderator.'))

    objects = SelectRelatedQuerySet.as_manager()

    class Meta:
        get_latest_by = 'last_posted'
        ordering = ('-sticky', '-last_posted',)

    def __str__(self):
        return self.subject

    @property
    def object(self):
        return self.forum.content_type.\
                get_object_for_this_type(pk=self.object_pk)

    @property
    def parent(self):
        return self.forum

    @property
    def object_template(self):
        """Returns a custom template if needed for this item."""
        custom_template = None
        if self.object_pk:
            ct = self.forum.content_type
            custom_template = '%s/%s_comments.html' % (ct.app_label, ct.model)

        elif self.forum.sync:
            conf = self.forum.sync_config
            key = conf.get('ENGINE', self.forum.sync).split('.')[-1]
            default = 'plugins/%s_comments.html' % key
            custom_template = conf.get('TEMPLATE', default)

        if custom_template is not None:
            try:
                get_template(custom_template)
                return custom_template
            except TemplateDoesNotExist:
                pass
        return 'forums/forumtopic_header.html'

    @property
    def comment_subject(self):
        if self.object_pk:
            return self.object
        return self

    @property
    def is_sticky(self):
        return bool(self.sticky)

    def get_absolute_url(self):
        return reverse('forums:topic', kwargs={'forum':self.forum.slug, 'slug':self.slug})

    def save(self, **kw):
        if not self.slug:
            self.slug = slugify(self.subject)
            while ForumTopic.objects.filter(slug=self.slug).count():
                self.slug = slugify(self.subject) + '_' + get_random_string(length=5)

        return super(ForumTopic, self).save(**kw)


class CommentLink(Model):
    """We extend our comment model with links to sync'd or imported comments"""
    comment = OneToOneField(Comment, related_name='link')

    message_id = CharField(max_length=255, db_index=True, unique=True,
            help_text="A unique identifier for this message")

    reply_id = CharField(max_length=255, null=True, blank=True, db_index=True,
            help_text="Either the previous message in the chain, or the parent id")

    subject = CharField(max_length=255, null=True, blank=True, db_index=True,
            help_text="A matchable subject line for this comment.")

    extra_data = TextField(null=True, blank=True)

    def __str__(self):
        return "%s: %s" % (self.source_id, self.message_id)

