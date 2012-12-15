"Inkscape project i18n code."

from django.conf import settings
from django.template.context import BaseContext
from django.http import HttpRequest, HttpResponseRedirect
from urlparse import urljoin
from django.utils.encoding import iri_to_uri
from django.utils.cache import patch_vary_headers
from django.utils import translation

import logging

__all__ = ('LocaleSubdomainMiddleware', 'langurl')


def langurl(language=None, location=None):
    """
    Builds an absolute URI from the language and location.

    ``location`` can be a string, relative or absolute (excluding protocol and
    server name), or blank if a request is specified. It can also be a request
    or template context containing a request, from which the current URL will
    be fetched.

    If the site is not being accessed from settings.HOST_ROOT, these URIs may
    be invalid or incorrect.
    """

    if isinstance(location, BaseContext):
        request = location.get('request', None)
        if request is None or not isinstance(location, HttpRequest):
            raise TypeError('build_absolute_uri() requires django.core.'
                    'context_processors.request to be installed or a '
                    'RequestContext if a Context is given')
    elif isinstance(location, HttpRequest):
        request = location
    else:
        request = None

    if request is None:
        root = '//'
        current_path = ''
    else:
        location = request.get_full_path()
        root = 'http%s://' % (request.is_secure() and 's' or '')
        current_path = request.path

    current_uri = (root + language + (language and '.') + settings.HOST_ROOT +
            current_path)
    location = urljoin(current_uri, location)

    return iri_to_uri(location)


class LocaleSubdomainMiddleware(object):
    """
    A modification a Django's django.middleware.locale.LocaleMiddleware, this
    looks at the subdomain first; if there is no subdomain (or www), it guesses
    the user's language and redirects them to the correct URL (naturally, any
    POST data in the request will be lost).

    It is important that a new setting, HOST_ROOT, be set. At present this is
    designed only for single-domain deployment. If others wish to use it
    outside the Inkscape project it will be extended to allow multi-site usage.
    If HOST_ROOT does not match the user's request, the user will be stuck in
    the default language.
    """

    def process_request(self, request):
        host = request.META.get('HTTP_HOST', '')
        dot_root = '.' + settings.HOST_ROOT
        if host == settings.HOST_ROOT or host.endswith(dot_root):
            subdomain = host[:len(host) - len(settings.HOST_ROOT)].rstrip('.')
            if subdomain in ('', 'www'):
                return self._request_autodetect(request)
            else:
                translation.activate(subdomain)
                request.LANGUAGE_CODE = translation.get_language()
                if request.LANGUAGE_CODE != subdomain:  # bad language subdomain
                    return self._request_autodetect(request)
        else:
            # Perhaps log that it was accessed from a different site and so was
            # stuck in English?
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = translation.get_language()

    def _request_autodetect(self, request):
        # Auto select and redirect
        language = translation.get_language_from_request(request)
        return HttpResponseRedirect(langurl(language, request))

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
