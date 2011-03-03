"""Site navigation rules."""
from django.utils.translation import ugettext_lazy as _


class leaf(object):
    __slots__ = ('title', 'href')

    def __init__(self, title, href):
        self.title = title
        self.href = href


class root(object):
    __slots__ = ('title', 'href', 'current', 'children')

    def __init__(self, title, href, children, current=False):
        self.title = title
        self.href = href
        self.children = children
        self.current = current

    def __iter__(self):
        return iter(self.children)

    def maybe_current(self, url):
        return (self.copy_as_current()
                if url == self.href or any(url == e.href for e in self) or
                url.startswith(self.href) else self)

    def copy_as_current(self):
        return root(self.title, self.href, self.children, True)


nav = (
        root(_('About'),                    '/about/', (
            leaf(_('Overview'),             '/about/'),
            leaf(_('Features'),             '/about/features/'),
            leaf(_('Screenshots'),          '/screenshots/'),
            leaf(_('Gallery'),              '/gallery/'),
            leaf(_('FAQ'),                  '/faq/'),
            leaf(_('User testimonials'),    '/about/testimonials/'),
            )),
        root(_('Download'),                 '/download/', (
            leaf(_('Official releases'),    '/download/'),
            leaf(_('Development versions'), '/download/development/'),
            leaf(_('Add-ons'),              '/download/addons/'),
            leaf(_('Clip art'),             '/download/clipart/'),
            )),
        root(_('Learn'),                    '/learn/', (
            leaf(_('User documentation'),   '/learn/documentation/'),
            leaf(_('Books'),                '/learn/books/'),
            leaf(_('Tutorials'),            '/learn/tutorials/'),
            leaf(_('Manuals'),              '/learn/manuals/'),
            leaf(_('Wiki'),                 '/learn/wiki/'),
            )),
        # Resources isn't ready yet.
        #root(_('Resources'),                '/resources/', (
            #leaf(_('Extensions'),           '/resources/extensions'),
            #leaf(_('Palettes'),             '/resources/palettes'),
            #leaf(_('Templates'),            '/resources/templates'),
            #leaf(_('Filters'),              '/resources/filters'),
            #)),
		# I've added Contact and Forums&Blogs as proposed sections --Pajarico
        root(_('Community'),                '/community/', (
            leaf(_('Get Involved'),         '/community/get-involved/'),
            leaf(_('Connect'),              '/community/connect/'),
            leaf(_('Forums & blogs'),       '/community/forums-and-blogs/'),
            leaf(_('Mailing lists'),        '/community/mailing-lists/'),
            leaf(_('Help & support'),       '/community/help/'),
            leaf(_('Contact'),              '/community/contact/'),
            leaf(_('Donate'),               '/donate/'),
            )),
        root(_('Developers'),               '/developers/', (
            leaf(_('Developer docs'),       '/developers/docs/'),
            leaf(_('Launchpad'),            'http://launchpad.net/inkscape'),
            leaf(_('Roadmap'),              '/developers/roadmap/'),
            leaf(_('Bazaar'),               '/developers/bazaar/'),
            leaf(_('Source code'),          '/developers/code/'),
            )),
        root(_('News'),                     '/news/', (
            leaf(_('Releases'),             '/news/category/releases/'),
            leaf(_('Contests'),             '/news/category/contests/'),
            leaf(_('Events'),               '/news/category/events/'),
            leaf(_('Press'),                '/news/category/press/'),
            )),
        )


def navigation_context_processor(request):
    url = request.META['PATH_INFO']
    return {'breadcrumb': get_breadcrumb(url),
            'nav': [r.maybe_current(url) for r in nav],
            'PAGE_ID': url[1:].replace('/', '-').rstrip('-') or 'front'}


def get_breadcrumb(url):
    for item in nav:
        if item.href == url:
            return ((), item)
        for subitem in item:
            if subitem.href == url:
                return ((item,), subitem)
