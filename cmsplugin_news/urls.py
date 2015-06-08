from django.conf.urls import *

from . import feeds
from . import views


urlpatterns = patterns('django.views.generic.date_based',
    url(r'^$',
        views.ArchiveIndexView.as_view(), name='news_archive_index'),

    url(r'^(?P<year>\d{4})/$',
        views.YearArchiveView.as_view(), name='news_archive_year'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        views.MonthArchiveView.as_view(), name='news_archive_month'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        views.DayArchiveView.as_view(), name='news_archive_day'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        views.DetailView.as_view(), name='news_detail'),

    url(r'^feed/$', feeds.NewsFeed(), name='news_rss'),
)

urlpatterns += patterns('cmsplugin_news.views',
    url(r'^create/',                'credit',   name="news_create"),
    url(r'^(?P<news_id>\d+)/edit/', 'credit',   name="news_edit"),
    url(r'^(?P<news_id>\d+)/del/',  'delete',   name="news_delete"),
    url(r'^(?P<news_id>\d+)/tr/',   'translate',name="news_translate"),
    url(r'^(?P<news_id>\d+)/',      'view',     name="news_item"),
)
