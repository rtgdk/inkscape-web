"""
This module hooks into django-cms' menu system by providing a clear menu
hierarchy for every news item.
"""
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from menus.menu_pool import menu_pool
from menus.base import NavigationNode
from cms.menu_bases import CMSAttachMenu
from cms.utils import get_language_from_request

from cmsplugin_news.models import News

from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NewsItemMenu(CMSAttachMenu):
    name = _("News menu")

    def get_nodes(self, request):
        return list(_get_nodes(request))

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def strf(t, f):
    return t.strftime(f.replace('%th', suffix(t.day)))

def _get_nodes(request):
    logger.debug("Rebuilding news menu")
    nodes = {}
    News.published.select_language( get_language_from_request(request) )

    for item in News.published.all():
        date = item.pub_date

        year_id = 'newsitem-year-%d' % date.year
        if year_id not in nodes:
            url = reverse('news_archive_year', kwargs=dict(year=date.year))
            nodes[year_id] = NavigationNode(date.year, url, year_id, visible=True)
            yield nodes[year_id]

        month_id = 'newsitem-month-%d.%d' % (date.year, date.month)
        if month_id not in nodes:
            url =  reverse('news_archive_month', kwargs=dict(year=date.year, month=strf(date, '%m')))
            nodes[month_id] = NavigationNode(_(strf(date, '%B')), url, month_id, year_id, visible=False)
            yield nodes[month_id]

        # This precision might be too much
        #day_id = 'newsitem-day-%d.%d.%d' % (date.year, date.month, date.day)
        #if day_id not in nodes:
        #    url = reverse('news_archive_day', kwargs=dict(year=date.year, month=strf(date, "%m"), day=strf(date, "%d")))
        #    nodes[day_id] = NavigationNode(strf(date, '%d%th'), url, day_id, month_id, visible=False)
        #    yield nodes[day_id]

        slug_id = 'newsitem-pk-%d' % item.pk
        if slug_id not in nodes:
            url = item.get_absolute_url()
            nodes[slug_id] = NavigationNode(item.title, url, slug_id, month_id, visible=False)
            yield nodes[slug_id]

menu_pool.register_menu(NewsItemMenu)
