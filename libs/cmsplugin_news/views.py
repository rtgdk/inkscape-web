from django.views import generic as generic_views
from django.shortcuts import redirect, render_to_response, RequestContext, _get_queryset
from django.shortcuts import get_object_or_404

from .settings import ARCHIVE_PAGE_SIZE
from .models import News
from .forms import NewsForm

from cms.utils import get_language_from_request
from django.db.models import Q

from datetime import datetime

def get_or_none(model, *args, **kwargs):
    queryset = _get_queryset(model)
    try:
        return queryset.get(*args, **kwargs)
    except model.DoesNotExist:
        return None

# Add permission here
def credit(request, news_id=None):
    existing = get_or_none(News, pk=news_id)

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            obj = form.save(commit=False)
            if not existing:
                obj.creator = request.user
                obj.created = datetime.now()
            else:
                obj.editor = request.user
                obj.edited = datetime.now()
            if request.POST.get('publish', False):
                obj.is_published = True
                obj.pub_date = datetime.now()
            obj.save()
            return redirect( obj.get_absolute_url() )
    else:
        form = NewsForm(instance=existing)
    return render_to_response('news/credit.html', { 'form' : form },
        context_instance=RequestContext(request))

# Add permission here
def view(request, news_id=None):
    news = News.objects.filter(pk=news_id)[0]
    return render_to_response('news/news_detail.html', { 'object' : news },
        context_instance=RequestContext(request))


class PublishedNewsMixin(object):
    """
    Since the queryset also has to filter elements by timestamp
    we have to fetch it dynamically.
    """
    def get_queryset(self):
        language = get_language_from_request(self.request)
        return News.published.filter( Q(language=language) ).all()

class ArchiveIndexView(PublishedNewsMixin, generic_views.ListView):
    """
    A simple archive view that exposes following context:

    * latest
    * date_list
    * paginator
    * page_obj
    * object_list
    * is_paginated

    The first two are intended to mimic the behaviour of the
    date_based.archive_index view while the latter ones are provided by
    ListView.
    """
    paginate_by = ARCHIVE_PAGE_SIZE
    template_name = 'news/news_archive.html'
    include_yearlist = True
    date_field = 'pub_date'

    def get_context_data(self, **kwargs):
        context = super(ArchiveIndexView, self).get_context_data(**kwargs)
        context['latest'] = context['object_list']
        if self.include_yearlist:
            date_list = self.get_queryset().dates('pub_date', 'year')[::-1]
            context['date_list'] = date_list
        return context


class DetailView(PublishedNewsMixin, generic_views.DateDetailView):
    template_name = 'news/news_detail.html'
    month_format = '%m'
    date_field = 'pub_date'
    allow_future = True

    def get_queryset(self):
        language = get_language_from_request(self.request)
        return News.published.all()

class MonthArchiveView(PublishedNewsMixin, generic_views.MonthArchiveView):
    template_name = 'news/news_archive_month.html'
    month_format = '%m'
    date_field = 'pub_date'


class YearArchiveView(PublishedNewsMixin, generic_views.YearArchiveView):
    template_name = 'news/news_archive_year.html'
    month_format = '%m'
    date_field = 'pub_date'


class DayArchiveView(PublishedNewsMixin, generic_views.DayArchiveView):
    template_name = 'news/news_archive_day.html'
    month_format = '%m'
    date_field = 'pub_date'

