"""
A module for managing news articles (essentially replacing the database).

This is not ready for use yet. It's like this because I couldn't be bothered
removing it from the commit ;-)  I wonder if anyone will ever notice this
message (while it's in the file or after it's been removed - looking at the bzr
history).  If you do, please email me and I shall think quite highly of your
observation. And sign you up to help if you haven't already done so.
"""

from django.conf import settings
from collections import defaultdict
import os
from .datatypes import load_article


class NewsManager(object):
    """
    A manager for news articles. This keeps track of categories, dates with
    posts, and more. It updates its catalogue via the ``update`` method.

    self.categories is a list of two-tuples, ('Category name', entry_count),
    sorted by entry count then lexicographic category name.

    """

    def __init__(self):
        self.update()

    def update(self):  # , path=None):
        """
        Architectural note:

            entries_by_year[year][slug][language] = Article()
            entries_by_category[category][year, slug][language] = Article()
        """

        entries_by_year = defaultdict(defaultdict(dict))
        entries_by_category = defaultdict(defaultdict(dict))

        for language in os.listdir(settings.NEWS_PATH):
            language_path = os.path.join(settings.NEWS_PATH, language)
            if not os.path.isdir(language_path):
                continue
            for year in os.listdir(language_path):
                try:
                    year = int(year)
                except TypeError:
                    continue  # This shouldn't ever happen
                year_path = os.path.join(language_path, year)
                if not os.path.isdir(year_path):
                    continue
                for slug in os.listdir(year_path):
                    if not slug.endswith('.rst'):
                        continue  # This shouldn't ever happen
                    slug = slug[:-4]  # Trim .rst
                    article = load_article(language, year, slug)
                    entries_by_year[year][slug][language] = article
                    entries_by_category[article.category][year, slug][language] = article

        # Updating the value in ``self`` is left to 
        self.entries_by_year = entries_by_year
        self.entries_by_category = entries_by_category

        self._update_cats_freqs()

    def _update_cats_freqs(self):
        self.categories = [(cat, len(entries))
                    for cat, entries in self.entries_by_category.iteritems()]
        self.categories.sort(key=lambda x: x[0])  # sort by category name
        self.categories.sort(key=lambda x: x[1])  # sort by frequency
