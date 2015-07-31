#
# PD - https://djangosnippets.org/snippets/2242/
#
"""
Limit the rate emails are sent to admins about errors
"""

import traceback
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
from datetime import datetime, timedelta


class RateLimitFilter(object):
    
    _errors = {}
        
    def filter(self, record):
        from django.conf import settings
        from django.core.cache import cache                               
        
        tb = '\n'.join(traceback.format_exception(*record.exc_info))

        # Track duplicate errors
        duplicate = False
        rate = getattr(settings, 'ERROR_RATE_LIMIT', 10)  # seconds
        if rate > 0:
            key = md5(tb).hexdigest()
            prefix = getattr(settings, 'ERROR_RATE_CACHE_PREFIX', 'ERROR_RATE')
            
            # Test if the cache works
            cache_key = '%s_%s' % (prefix, key)
            try:
                cache.set(prefix, 1, 1)
                use_cache = cache.get(prefix) == 1
            except:
                use_cache = False
            
            if use_cache:
                duplicate = cache.get(cache_key) == 1
                cache.set(cache_key, 1, rate)
            else:
                min_date = datetime.now() - timedelta(seconds=rate)
                max_keys = getattr(settings, 'ERROR_RATE_KEY_LIMIT', 100)
                duplicate = (key in self._errors and self._errors[key] >= min_date)
                self._errors = dict(filter(lambda x: x[1] >= min_date, 
                                          sorted(self._errors.items(), 
                                                 key=lambda x: x[1]))[0-max_keys:])
                if not duplicate:
                    self._errors[key] = datetime.now()

        return not duplicate
