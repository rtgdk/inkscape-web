"""Site navigation rules."""
from django.utils.translation import ugettext_lazy as _
import re
from django.conf import settings
from django.contrib import messages
from django.utils.safestring import mark_safe


class node(object):
    __slots__ = ('title', 'href', 'current', 'children')

    def __init__(self, title, href, children=(), current=False):
        self.title = title
        self.href = href
        self.children = children
        self.current = current

    def __iter__(self):
        return iter(self.children)

    def maybe_current(self, url):
        return (self.copy_as_current()
                if url == self.href or any(url == e.href for e in self) or
                url.startswith(self.href) or any(url.startswith(e.href) for e in self) else self)

    def copy_as_current(self):
        return node(self.title, self.href, self.children, True)


nav = (
        node(_('About'),                    '/about/', (
            node(_('Overview'),             '/about/'),
            node(_('Features'),             '/about/features/'),
            node(_('Screenshots'),          '/screenshots/'),
            node(_('Gallery'),              '/gallery/'),
            node(_('FAQ'),                  '/faq/'),
            node(_('User testimonials'),    '/about/testimonials/'),
            )),
        node(_('Download'),                 '/download/', (
            node(_('Official releases'),    '/download/'),
            node(_('Development versions'), '/download/development/'),
            node(_('Add-ons'),              '/download/addons/'),
            node(_('Clip art'),             '/download/clipart/'),
            )),
        node(_('Learn'),                    '/learn/', (
            node(_('User documentation'),   '/learn/documentation/'),
            node(_('Books'),                '/learn/books/'),
            node(_('Tutorials'),            '/learn/tutorials/'),
            node(_('Manuals'),              '/learn/manuals/'),
            node(_('Wiki'),                 '/learn/wiki/'),
            )),
        # Resources isn't ready yet.
        #node(_('Resources'),                '/resources/', (
            #node(_('Extensions'),           '/resources/extensions'),
            #node(_('Palettes'),             '/resources/palettes'),
            #node(_('Templates'),            '/resources/templates'),
            #node(_('Filters'),              '/resources/filters'),
            #)),
		# I've added Contact and Forums&Blogs as proposed sections --Pajarico
        node(_('Community'),                '/community/', (
            node(_('Get Involved'),         '/community/get-involved/'),
            node(_('Connect'),              '/community/connect/'),
            node(_('Forums & blogs'),       '/community/forums-and-blogs/'),
            node(_('Mailing lists'),        '/community/mailing-lists/'),
            node(_('Help & support'),       '/community/help/'),
            node(_('Contact'),              '/community/contact/'),
            node(_('Donate'),               '/donate/'),
            )),
        node(_('Developers'),               '/developers/', (
            node(_('Developer docs'),       '/developers/docs/'),
            node(_('Launchpad'),            'http://launchpad.net/inkscape'),
            node(_('Roadmap'),              '/developers/roadmap/'),
            node(_('Bazaar'),               '/developers/bazaar/'),
            node(_('Source code'),          '/developers/code/'),
            )),
        node(_('News'),                     '/news/', (
            node(_('Releases'),             '/news/category/releases/'),
            node(_('Contests'),             '/news/category/contests/'),
            node(_('Events'),               '/news/category/events/'),
            node(_('Press'),                '/news/category/press/'),
            )),
        )

extra_nav = (
        node(_('Showcase'), '/showcase/', (
            node(_('Branding'),   '/showcase/branding/'),
            node(_('Icons'),      '/showcase/icons/'),
            node(_('Web design'), '/showcase/web-design/'),
            node(_('CD booklet'), '/showcase/cd-booklet/'),
            )),
        )


class RegexTuple(tuple):
    def __contains__(self, other):
        return any(re.search(s, other) for s in self)


valid_breadcrumbless_urls = RegexTuple((
            re.compile('^/$'),
            re.compile('^/news/'),
        ))

def navigation_context_processor(request):
    url = request.META['PATH_INFO']
    return {'breadcrumb': get_breadcrumb(url, request),
            'nav': [r.maybe_current(url) for r in nav],
            'PAGE_ID': url[1:].replace('/', '-').rstrip('-') or 'front'}


def get_breadcrumb(url, request=None):
    for n in (nav, extra_nav):
        for item in n:
            breadcrumb = get_breadcrumb_nested(url, item, [])
            if breadcrumb is not None:
                return breadcrumb
    if url not in valid_breadcrumbless_urls and settings.DEBUG and request:
        messages.error(request, mark_safe('Developer warning: no breadcrumb found for URL <code>%s</code>.' % url))

def get_breadcrumb_nested(url, item, trail):
    if item.href == url:
        return (trail, item)
    for subitem in item:
        trail.append(item)
        i = get_breadcrumb_nested(url, subitem, trail)
        if i is not None:
            return i
        trail.pop()
