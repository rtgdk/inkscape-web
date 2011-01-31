from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.template.loader import get_template_from_string
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils._os import safe_join
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
import os
from docutils.core import publish_parts
from . import rst


def front_page(request):
    return direct_to_template(request, 'front.html')


#def download_page(request):
#    return direct_to_template(request, 'download.html')


def load_page(request, url):
    try:
        return _load_page(request, url, request.LANGUAGE_CODE)
    except Http404:
        return _load_page(request, url, 'en',
        # Translators: replace "the current language" with the language name
                mark_safe(_('This page is not available in English. Here is '
                    'the English version of this page. If you would like to '
                    'help with translating this website, please '
                    '<a href="">contact us</a>.')))


def _load_page(request, url, language, message=None):
    try:
        full_path = safe_join(os.path.abspath(os.path.join(
            settings.CONTENT_PATH, language)), url)
    except ValueError:  # They've tried something like ../
        return HttpResponseBadRequest("No cheating.")

    if os.path.exists(full_path + '.html'):
        if message:
            messages.info(request, message)
        return _load_djhtml_page(request, full_path + '.html')
    elif os.path.exists(full_path + '.rst'):
        if message:
            messages.info(request, message)
        return _load_rst_page(request, full_path + '.rst')
    else:
        raise Http404('No content with this name.')



def _load_rst_page(request, path):
    with open(path) as content:
        text = content.read()

    parts = publish_parts(
            source=text,
            settings_overrides=getattr(settings, 'RST_SETTINGS_OVERRIDES', {}),
            writer_name='html')

    return direct_to_template(request, 'normal.html', {'title':
        mark_safe(parts['title']), 'text': mark_safe(parts['html_body'])})


def _load_djhtml_page(request, path):
    with open(path) as content:
        t = get_template_from_string(content.read())
        return HttpResponse(t.render(RequestContext(request)))
