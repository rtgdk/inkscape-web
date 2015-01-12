
from haystack.indexes import *
from .models import Resource

class ResourceIndex(SearchIndex, Indexable):
    text      = CharField(document=True, use_template=True)

    edited    = DateTimeField(model_attr='edited')
    created   = DateTimeField(model_attr='created')
    published = BooleanField(model_attr='published')

    def get_model(self):
        return Resource

    def get_updated_field(self):
        return 'edited'

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(published=True)

from .views import GalleryList
from pile.search_base import add_fields

# This adds the extra indexable fields that the category list uses.  
add_fields(ResourceIndex, GalleryList)


