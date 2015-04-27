
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from .forms import FeedbackForm
from .models import ErrorLog

from django.conf import settings
from django.core.mail import send_mail

def contact_us(request):
    form = FeedbackForm(request.POST or None)
    if form.is_valid():
        sender = 'Anonymous User <unknown@inkscape.org>'
        if request.user.is_authenticated():
            sender = request.user.email
            if request.user.first_name:
                sender = '%s %s <%s>' % (request.user.first_name, request.user.last_name, request.user.email)
        recipients = [ "%s <%s>" % (a,b) for (a,b) in settings.ADMINS ]
        send_mail("Website Feedback", form.cleaned_data['comment'], sender, recipients)
        return render_to_response('feedback.html', {}, RequestContext(request))
    return render_to_response('feedback.html', { 'form': form }, RequestContext(request))   


def robots(request):
    return render_to_response('robots.txt', {},
        context_instance=RequestContext(request), content_type='text/plain')

def errors(request):
    return render_to_response('error/list.html', {
      'errors': ErrorLog.objects.all().order_by('-count')
    }, RequestContext(request))

def error(request, **c):
    error = c['error']
    response = render_to_response('error/%s.html' % error, c,
        context_instance=RequestContext(request))
    if not settings.DEBUG or error != '404':
        ErrorLog.objects.get_or_create(uri=request.get_full_path(), status=int(error))[0].add()
        response.status_code = int(c['error'])
    return response

def error403(request):
    return error(request, error='403', title=_('Permission Denied'))

def error404(request):
    return error(request, error='404', title=_('Page Not Found'))

def error500(request):
    return error(request, error='500', title=_('Server Error'))

from haystack.forms import SearchForm
from haystack.query import SearchQuerySet, SQ
from haystack.views import SearchView as BaseView

from cms.utils import get_language_from_request

class SearchView(BaseView):
    """Restrict the search to the selected language only"""
    template = "search/search.html"
    searchqueryset = SearchQuerySet()
    results_per_page = 20
    form_class = SearchForm

    def __call__(self, request):
        language = get_language_from_request(request)
        self.searchqueryset = SearchQuerySet().filter(language=language)
        return BaseView.__call__(self, request)

