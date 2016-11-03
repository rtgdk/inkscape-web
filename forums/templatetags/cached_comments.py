#
# Copyright (C) 2016, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Just like the comments templatetag from django_comments but tracks the
queryset for the caching middleware to pick up.
"""

from django.template.base import Library
from django_comments.templatetags.comments import CommentListNode

from inkscape.middleware import TrackCacheMiddleware

register = Library()

class CachedCommentListNode(CommentListNode):
    def render(self, context):
        request = context['request']
        if hasattr(request, 'cache_tracks'):
            qs = self.comment
            ctype, object_pk = self.get_target_ctype_pk(context)
            if object_pk:
                qs = self.comment_model.objects.filter(
                      content_type=ctype,
                      object_pk=str(object_pk),
                   )
		request.cache_tracks.append(qs)
        return super(CachedCommentListNode, self).render(context)

@register.tag
def get_cached_comment_list(parser, token):
    """ 
    See django_comments.templatetags.comments.get_comment_list
    """
    return CachedCommentListNode.handle_token(parser, token)

