
import datetime
from haystack.indexes import *
from cmsplugin_news.models import News

class NewsIndex(SearchIndex, Indexable):
    text     = CharField(document=True, use_template=True)
    pub_date = DateTimeField(model_attr='pub_date')
    language = CharField(stored=True, model_attr='lang')

    def get_model(self):
        return News

    def get_updated_field(self):
        return 'pub_date'

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(is_published=True)

