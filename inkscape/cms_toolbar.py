from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar

from cms.constants import LEFT, RIGHT
from django.conf import settings

@toolbar_pool.register
class LiveToolbar(CMSToolbar):
    """Show a NOT LIVE! warning to users when on localhost or staging"""
    def populate(self):
        if settings.DEBUG:
            # A full menu is not possible with our extra class for flashing red thing.
            #menu = self.toolbar.get_or_create_menu('live', _('NOT LIVE!'), position=0)
            url = 'https://inkscape.org%s' % self.request.path
            self.toolbar.add_link_item(_('NOT LIVE!'), url=url, extra_classes=['debugwarn'], position=0)
            # XXX Add a "Time until next refresh" option here.

@toolbar_pool.register
class SubscribeToolbar(CMSToolbar):
    """Displace a Subscribe to this page link."""
    def populate(self):
        if not self.request.current_page:
            return
        menu = self.toolbar.get_or_create_menu('subscribe', _('Subscribe'))
        url = reverse('alert.subscribe', kwargs={'slug': "cms_page_published", 'pk': self.request.current_page.pk})
        menu.add_link_item(_('To This Page Only'), url=url)
        url = reverse('alert.subscribe', kwargs={'slug': "cms_page_published"})
        menu.add_link_item(_('To All Pages'), url=url)
        # XXX We could check existing subscriptions here

