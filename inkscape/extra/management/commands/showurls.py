#
# Copyright Martin Owens 2013
#
# AGPLv3
#
"""
Shows all the available urls for a django website, useful for debugging.
"""

import urls

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = '<start_url>'
    help = 'Shows all urls begining with the start_url'

    def handle(self, *args, **options):
        self.start_url = None
        if len(args) > 0:
            self.start_url = args[0]
        self.show_urls(urls.urlpatterns)

    def urls_name(self, uc):
        if isinstance(uc, list) and uc:
            return self.urls_name(uc[0])
        elif hasattr(uc, '__file__'):
            return uc.__file__.split('../')[-1].split('site-packages/')[-1][:-1]
        return None

    def show_urls(self, urllist, depth=0):
        d = "  " * depth
        for entry in urllist:
            p = entry.regex.pattern
            if hasattr(entry, 'url_patterns'):
                name = None
                if hasattr(entry, '_urlconf_module'):
                    name = self.urls_name(entry._urlconf_module)
                self.show_urls(entry.url_patterns, depth + 1)
                if name:
                    self.stdout.write("%s%s > %s" % ( d, p, name ))
            else:
                name = entry.__dict__.get('name', '[Undefined]') or '[Unnammed]'
                self.stdout.write("%s'%s' | %s" % ( d, name, p))




