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
Watches for comments so they can be registered.
"""

from django.apps import AppConfig
from django.dispatch import receiver
from django.db.models.signals import post_save

from django_comments.models import Comment

def post_create(model, fn):
    def _inner(sender, instance, created=False, **kw):
        if created:
            fn(instance, **kw)
    post_save.connect(_inner, sender=model, weak=False)


class ForumsConfig(AppConfig):
    name = 'forums'

    def ready(self):
        from .models import Forum

        post_create(Comment, self.new_comment)
        post_create(Forum, self.new_forum)

    def new_forum(self, instance, **kw):
        """Called when a new forum is created"""
        done = []
        if instance.content_type:
            # Look for all existing comments that might exist for this object
            cms = Comment.objects.filter(content_type=instance.content_type)
            for comment in cms.order_by('-submit_date'):
                if comment.object_pk not in done:
                    self.new_comment(comment)
                    done.append(comment.object_pk)

    def new_comment(self, instance, **kw):
        """Called when a new comment has been saved"""
        from .models import Forum, ForumTopic
        defaults = {'subject': unicode(instance.content_object)}

        for forum in Forum.objects.filter(content_type=instance.content_type):
            try:
                (topic, _) = ForumTopic.objects.get_or_create(forum_id=forum.pk,
                                  object_pk=instance.object_pk, defaults=defaults)
            except ForumTopic.MultipleObjectsReturned:
                continue

            for obj in (forum, topic):
                if not obj.last_posted or obj.last_posted < instance.submit_date:
                    obj.last_posted = instance.submit_date
                    obj.save(update_fields=['last_posted'])
            

