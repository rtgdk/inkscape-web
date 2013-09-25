
from . import settings

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from cmsplugin_brochure.models import Brochure, BrochureItem

class BrochureFeed(Feed):
    title = settings.FEED_TITLE
    description = settings.FEED_DESCRIPTION

    title_template = 'brochure/feeds/item_title.html'
    description_template = 'brochure/feeds/item_description.html'

    def get_object(self, request, brochure_id):
        return get_object_or_404(Brochure, pk=brochure_id)

    def items(self, obj):
        return obj.items()[:settings.FEED_SIZE]

    def title(self, obj):
        return obj.title

    def description(self, obj):
        return obj.description

    def link(self, obj):
        return obj.link

    def item_link(self, item):
        return item.link

    def item_pubdate(self, item):
        return item.publish
