
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.template import RequestContext

from .models import Revision, RevisionDiff

class ViewDiff(DetailView):
    model = Revision
    template_name = "cms/revision_diff.html"


