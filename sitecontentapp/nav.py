"""Site navigation rules."""
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
                if url == self.href or any(url == e.href for e in self)
                else self)

    def copy_as_current(self):
        return root(self.title, self.href, self.children, True)


nav = (
        root('About',                    '/about/', (
            leaf('Overview',             '/about/'),
            leaf('Features',             '/about/features'),
            leaf('Screenshots',          '/screenshots'),
            leaf('Gallery',              '/gallery'),
            leaf('FAQ',                  '/faq'),
            leaf('User testimonials',    '/about/testimonials'),
            )),
        root('Download',                 '/download/', (
            leaf('Official releases',    '/download/'),
            leaf('Development versions', '/download/development'),
            leaf('Add-ons',              '/download/addons'),
            leaf('Clip art',             '/download/clipart'),
            )),
        root('Learn',                    '/learn/', (
            leaf('User documentation',   '/learn/documentation'),
            leaf('Books',                '/learn/books'),
            leaf('Tutorials',            '/learn/tutorials'),
            leaf('Manuals',              '/learn/manuals'),
            leaf('Wiki',                 '/learn/wiki'),
            )),
        # Resources isn't ready yet.
        #root('Resources',                '/resources/', (
            #leaf('Extensions',           '/resources/extensions'),
            #leaf('Palettes',             '/resources/palettes'),
            #leaf('Templates',            '/resources/templates'),
            #leaf('Filters',              '/resources/filters'),
            #)),
        root('Community',                '/community/', (
            leaf('Get Involved',         '/community/get-involved'),
            leaf('Connect',              '/community/connect'),
            leaf('Mailing lists',        '/community/mailing-list'),
            leaf('Help & support',       '/community/help'),
            leaf('Donate',               '/donate'),
            )),
        root('Developers',               '/developers/', (
            leaf('Developer docs',       '/developers/docs'),
            leaf('Launchpad',            'http://launchpad.net/inkscape'),
            leaf('Roadmap',              '/developers/roadmap'),
            leaf('Bazaar',               '/developers/bazaar'),
            leaf('Source code',          '/developers/code'),
            )),
        root('News',                     '/news/', (
            leaf('Releases',             '/news/releases'),
            leaf('Contests',             '/news/contests'),
            leaf('Events',               '/news/events'),
            leaf('Press',                '/news/press'),
            )),
        )


def NavigationContextProcessor(request):
    url = request.META['PATH_INFO']
    return {'breadcrumb': get_breadcrumb(url),
            'nav': [r.maybe_current(url) for r in nav],
            'PAGE_ID': url[1:].replace('/', '-').rstrip('-') or 'front'}

def get_breadcrumb(url):
    for item in nav:
        if item.href == url:
            return ((),item)
        for subitem in item:
            if subitem.href == url:
                return ((item,), subitem)
