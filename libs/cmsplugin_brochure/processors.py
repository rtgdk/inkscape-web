
from django.core.files import File, temp

import os
import sys
import urllib2

from feedparser import parse as rss_parse

def download_nail(url):
    img_temp = temp.NamedTemporaryFile(delete=True)
    img_temp.write(urllib2.urlopen(url).read())
    img_temp.flush()
    return File(img_temp)

def get_thumbnail(nails):
    """Return the best image that fits our settings"""
    for url, width, height in nails:
        return download_nail(url)
    return (None, None)

def rss_nails(media):
    for u in media:
        yield (u['url'], u['width'], u['heigh'])

def rss(src):
    feed = rss_parse(src.data)
    if not feed:
        return "Can't find feed [ERROR]"
    publish = datetime(*feed.feed.published_parsed[:-3]),
    if src.publish and src.publish >= publish:
        return "Already up to date [SKIP]"

    for item in feed.entries:
        ipub = datetime(*item.published_parsed[:-3])
        if ipub < src.publish:
            sys.stderr.write("Skipping old entry")
            continue

        (name, thumb) = get_thumbnail(rss_nails(item.media_thumbnail)),
        if not name or not thumb:
            sys.stderr.write("Skipping, no thumbnail")
            continue

        src.brochureitem_set.create(
            title   = item.title,
            desc    = item.description,
            publish = ipub,
            thumb   = (name, thumb),
        )

    src.publish = publish
    src.save()

