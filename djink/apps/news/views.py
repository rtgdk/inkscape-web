from django.http import Http404
from django.views.generic.simple import direct_to_template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from .manager import news_manager
from ...nav import node

PAGE_SIZE = 4


def _archive(request, articles, breadcrumb=None, title=None, page_title=None):
    articles.sort(key=lambda x: x.date, reverse=True)
    if title is None and page_title is None:
        title = _('News')
        page_title = _('Inkscape News')
    elif title is None:
        title = _('News')
    elif page_title is None:
        page_title = title

    try:
        page_num = int(request.GET.get('page', 1))
    except ValueError:
        page_num = 1

    paginator = Paginator(articles, PAGE_SIZE)

    try:
        page = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    kwargs = {
        'articles': page,
        'title': title,
        'page_title': page_title,
        'categories': [dict(name=name, count=count)
            for name, count in news_manager.categories],
        'archives': sorted(news_manager.articles_by_year.keys(), reverse=True),
        }

    if breadcrumb:
        kwargs['breadcrumb_override'] = breadcrumb
    return direct_to_template(request, 'news_archive.html', kwargs)


def archive_all(request):
    return _archive(request, news_manager.get_articles(request.LANGUAGE_CODE))


def archive_year(request, year):
    try:
        year = int(year)
    except ValueError:
        pass
    return _archive(
            request=request,
            articles=news_manager.get_articles(request.LANGUAGE_CODE,
                news_manager.articles_by_year.get(year, {}).values()),
            breadcrumb=((node(_('News'), '/news/'),), node(year, '')),
            title=_('%s News') % year,
            page_title=_('Inkscape News in %s') % year)


def article(request, year, slug):
    try:
        article, local_lang = news_manager.get_article(year, slug,
                request.LANGUAGE_CODE)
    except KeyError:
        raise Http404('No such news item.')

    if not local_lang:
        messages.info(request,
                # Translators: replace "the current language" with the language
                # name
                mark_safe(_('This page is not available in English. Here is '
                    'the English version of this page. If you would like to '
                    'help with translating this website, please '
                    '<a href="">contact us</a>.')))

    return direct_to_template(request, 'news_full.html', {
        'title': article.title,
        'article': article,
        'breadcrumb_override': ((node(_('News'), '/news/'),
    node(year, '/news/%s/' % year)), node(article.title, '')),
        'categories': [dict(name=name, count=count)
            for name, count in news_manager.categories],
        'archives': news_manager.articles_by_year.keys(),
        })


def category(request, slug):
    if slug not in news_manager.category_slugs:
        raise Http404('Category with slug %r does not exist' % slug)
    friendly_name = news_manager.category_slugs[slug]

    return _archive(request,
            articles=news_manager.get_articles(request.LANGUAGE_CODE,
                news_manager.articles_by_category.get(friendly_name,
                    {}).values()),
            breadcrumb=((node(_('News'), '/news/'),), node(friendly_name, '')),
            title=_('News: %s') % friendly_name,
            page_title=_('Inkscape News: %s') % friendly_name)
