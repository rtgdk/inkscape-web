
from django.utils.timezone import now

class SetLastVisitMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            request.user.details.last_seen = now()
            request.user.details.save()

