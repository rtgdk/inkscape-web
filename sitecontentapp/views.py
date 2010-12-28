from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.template.loader import get_template_from_string
from django.conf import settings
from django.core.urlresolvers import Resolver404
from django.utils import safestring
from django.utils._os import safe_join
import os
from docutils.core import publish_parts
from . import rst


def front_page(request):
    return direct_to_template(request, 'front.html')


#def download_page(request):
#    return direct_to_template(request, 'download.html')


def load_page(request, url):
    try:
        full_path = safe_join(os.path.abspath(os.path.join(
            settings.CONTENT_PATH, request.LANGUAGE_CODE)), url)
    except ValueError:  # They've tried something like ../
        return HttpResponseBadRequest("No cheating.")

    if os.path.exists(full_path + '.html'):
        return _load_djhtml_page(request, full_path + '.html')
    #elif os.path.exists(full_path + '.html'):
    #    title, text = 'TODO', _load_html_page(full_path + '.html')
    elif os.path.exists(full_path + '.rst'):
        title, text = _load_rst_page(full_path + '.rst')

    else:
        raise Http404('No content with this name.')

    return direct_to_template(request, 'normal.html',
            {'title': title, 'text': text})


def _load_rst_page(path):
    with open(path) as content:
        text = content.read()

    parts = publish_parts(
            source=text,
            settings_overrides=getattr(settings, 'RST_SETTINGS_OVERRIDES', {}),
            writer_name='html')

    return (safestring.mark_safe(parts['title']),
            safestring.mark_safe(parts['html_body']))


def _load_djhtml_page(request, path):
    with open(path) as content:
        t = get_template_from_string(content.read())
        return HttpResponse(t.render(RequestContext(request)))
