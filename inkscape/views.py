from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from django.utils.translation import ugettext_lazy as _

def error(request, **c):
    response = render_to_response('error/%s.html' % c['error'], c,
        context_instance=RequestContext(request))
    response.status_code = int(c['error'])
    return response

def error403(request):
    return error(request, error='403', title=_('Permission Denied'))

def error404(request):
    return error(request, error='404', title=_('Page Not Found'))

def error500(request):
    return error(request, error='500', title=_('Server Error'))

