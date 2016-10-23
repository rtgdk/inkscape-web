

#
# This script was used to update resources to published and email all users effected.
#


from resources.models import Resource
from django.utils.timezone import now
from datetime import timedelta

import time

resources = Resource.objects.filter(created__lt=now()-timedelta(days=14), published=False)

for user in set([res.user for res in resources]):
    rec = resources.filter(user_id=user.pk)
    msg = """

Dear %s,

The website has upgraded it's publishing user interface to make it more obvious when uploads are published. There are quite a few older uploads which are not published after a long time. So we're automatically setting uploads to published if they were uploaded more than two weeks ago. Please see the list below of items from your gallery that have been effected:

%s

""" % (unicode(user), "\n".join([" * %s (%s) https://inkscape.org%s" % (unicode(r), str(r.created), r.get_absolute_url()[3:]) for r in rec]))
    rec.update(published=True)
    try:
        user.email_user("Uploads Automatically Published", msg, from_email="webmaster@inkscape.org")
    except:
        print "Error sending email."
    print user
    time.sleep(0.5)

