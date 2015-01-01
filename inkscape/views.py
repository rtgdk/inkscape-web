from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

def error(request, **c):
    error = c['error']
    response = render_to_response('error/%s.html' % error, c,
        context_instance=RequestContext(request))
    if not settings.DEBUG or error != '404':
        response.status_code = int(c['error'])
    return response

def error403(request):
    return error(request, error='403', title=_('Permission Denied'))

def error404(request):
    return error(request, error='404', title=_('Page Not Found'))

def error500(request):
    return error(request, error='500', title=_('Server Error'))

