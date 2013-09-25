
import datetime
from haystack import indexes
from cmsplugin_brochure.models import BrochureItem

class BrochureIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    pub_date = indexes.DateTimeField(model_attr='pub_date')
    language = indexes.CharField(stored=True, model_attr='language')

    def get_model(self):
        return BrochureItem

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(is_published=True)

