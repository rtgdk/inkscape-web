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


def load_page(request, url, prefix=None):
    if prefix:
        url = prefix + url
    template = os.path.join('content', url+'.html')
    return direct_to_template(request, template)
    




