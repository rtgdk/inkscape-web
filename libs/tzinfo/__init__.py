#
# I may expand this to replace the entire python festering datetime module.
#

from datetime import datetime, tzinfo, timedelta
from time import mktime

class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return timedelta(0)

utc = UTC()

def datetimetz(struct):
    return datetime.fromtimestamp(mktime(struct)).replace(tzinfo=utc)

