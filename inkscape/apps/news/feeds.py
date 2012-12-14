import datetime
from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from .manager import news_manager


# For the get_feed override
from django.conf import settings
from django.template import loader, TemplateDoesNotExist, RequestContext
from django.utils import feedgenerator, tzinfo
from django.utils.encoding import smart_unicode
from django.contrib.sites.models import get_current_site
from django.contrib.syndication.views import add_domain



class LatestNewsFeed(Feed):
    title = _('Inkscape News')
    link = '/news/'
    description = _('News about the Inkscape scalable vector graphics editor')

    def get_object(self, request):
        return request.LANGUAGE_CODE

    def items(self, lang):
        # lang is obj
        articles = [a['en' if 'en' in a else lang]
                for a in news_manager.articles if 'en' in a or lang in a]
        articles.sort(key=lambda x: x.date, reverse=True)
        return articles[:8]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body

    def item_link(self, item):
        return reverse('news:article', args=[item.date.year, item.slug])

    def item_author_name(self, item):
        return item.author

    def item_pubdate(self, item):
        return datetime.datetime.combine(item.date, datetime.time())

    def item_categories(self, item):
        return (item.category,)

    def language(self, obj):
        return obj  # request.LANGUAGE_CODE

    # Regretably, I'm required to copy all this from
    # django.contrib.syndication.views.Feed purely to override "language =
    # settings.LANGUAGE_CODE.decode()".  Applied patch as per
    # http://code.djangoproject.com/ticket/13896 for forwards compatibility.
    def get_feed(self, obj, request):
        """
        Returns a feedgenerator.DefaultFeed object, fully populated, for
        this feed. Raises FeedDoesNotExist for invalid parameters.
        """
        current_site = get_current_site(request)

        link = self._Feed__get_dynamic_attr('link', obj)
        link = add_domain(current_site.domain, link, request.is_secure())

        feed = self.feed_type(
            title = self._Feed__get_dynamic_attr('title', obj),
            subtitle = self._Feed__get_dynamic_attr('subtitle', obj),
            link = link,
            description = self._Feed__get_dynamic_attr('description', obj),
            language = self._Feed__get_dynamic_attr('language', obj,
                settings.LANGUAGE_CODE.decode()),
            feed_url = add_domain(
                current_site.domain,
                self._Feed__get_dynamic_attr('feed_url', obj) or request.path,
                request.is_secure(),
            ),
            author_name = self._Feed__get_dynamic_attr('author_name', obj),
            author_link = self._Feed__get_dynamic_attr('author_link', obj),
            author_email = self._Feed__get_dynamic_attr('author_email', obj),
            categories = self._Feed__get_dynamic_attr('categories', obj),
            feed_copyright = self._Feed__get_dynamic_attr('feed_copyright', obj),
            feed_guid = self._Feed__get_dynamic_attr('feed_guid', obj),
            ttl = self._Feed__get_dynamic_attr('ttl', obj),
            **self.feed_extra_kwargs(obj)
        )

        title_tmp = None
        if self.title_template is not None:
            try:
                title_tmp = loader.get_template(self.title_template)
            except TemplateDoesNotExist:
                pass

        description_tmp = None
        if self.description_template is not None:
            try:
                description_tmp = loader.get_template(self.description_template)
            except TemplateDoesNotExist:
                pass

        for item in self._Feed__get_dynamic_attr('items', obj):
            if title_tmp is not None:
                title = title_tmp.render(RequestContext(request, {'obj': item, 'site': current_site}))
            else:
                title = self._Feed__get_dynamic_attr('item_title', item)
            if description_tmp is not None:
                description = description_tmp.render(RequestContext(request, {'obj': item, 'site': current_site}))
            else:
                description = self._Feed__get_dynamic_attr('item_description', item)
            link = add_domain(
                current_site.domain,
                self._Feed__get_dynamic_attr('item_link', item),
                request.is_secure(),
            )
            enc = None
            enc_url = self._Feed__get_dynamic_attr('item_enclosure_url', item)
            if enc_url:
                enc = feedgenerator.Enclosure(
                    url = smart_unicode(enc_url),
                    length = smart_unicode(self._Feed__get_dynamic_attr('item_enclosure_length', item)),
                    mime_type = smart_unicode(self._Feed__get_dynamic_attr('item_enclosure_mime_type', item))
                )
            author_name = self._Feed__get_dynamic_attr('item_author_name', item)
            if author_name is not None:
                author_email = self._Feed__get_dynamic_attr('item_author_email', item)
                author_link = self._Feed__get_dynamic_attr('item_author_link', item)
            else:
                author_email = author_link = None

            pubdate = self._Feed__get_dynamic_attr('item_pubdate', item)
            if pubdate and not pubdate.tzinfo:
                ltz = tzinfo.LocalTimezone(pubdate)
                pubdate = pubdate.replace(tzinfo=ltz)

            feed.add_item(
                title = title,
                link = link,
                description = description,
                unique_id = self._Feed__get_dynamic_attr('item_guid', item, link),
                enclosure = enc,
                pubdate = pubdate,
                author_name = author_name,
                author_email = author_email,
                author_link = author_link,
                categories = self._Feed__get_dynamic_attr('item_categories', item),
                item_copyright = self._Feed__get_dynamic_attr('item_copyright', item),
                **self.item_extra_kwargs(item)
            )
        return feed
