
from ajax_select import LookupChannel
from .models import Tag

class TagLookup(LookupChannel):
    model = Tag
    min_length = 0

    def get_query(self, q, request):
        return Tag.objects.all()

