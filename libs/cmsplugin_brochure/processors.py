#
# Copyright 2013(c) Martin Owens <mail@doctormo.org>
#
# Licensed: AGPLv3
#

import os
import sys
import urllib2

from time import mktime
from datetime import datetime, tzinfo, timedelta
from feedparser import parse as rss_parse

from django.core.files import File, temp
from tzinfo import utc, datetimetz

def download_nail(url):
    img_temp = temp.NamedTemporaryFile(delete=True)
    img_temp.write(urllib2.urlopen(url).read())
    img_temp.flush()
    return File(img_temp)

def get_thumbnail(nails):
    """Return the best image that fits our settings"""
    for url, width, height in nails:
        if url:
            name = url.split('/')[-1]
            return name, download_nail(url)
    return None, None

def rss_nails(media):
    for u in media:
        yield (u.get('url', None), u.get('width', 0), u.get('height',0))


def rss(src):
    feed = rss_parse(src.data)
    indexed = datetime.now().replace(tzinfo=utc)
    if not feed:
        return "Can't find feed [ERROR]"
    if feed.feed.has_key('published_parsed'):
        publish = datetimetz(feed.feed.published_parsed)
        if src.publish and src.publish >= publish:
            return "Already up to date [SKIP]"
    else:
        publish = indexed

    BrochureItem = src.brochureitem_set.model

    for entry in feed.entries:
        entered = datetimetz(entry.published_parsed)
        if src.publish and entered < src.publish:
            sys.stderr.write("Skipping old entry\n")
            continue

        (name, thumb) = (None, None)
        if entry.has_key('media_thumbnail'):
            (name, thumb) = get_thumbnail(rss_nails(entry.media_thumbnail))
        elif entry.has_key('thumbnail'):
            (name, thumb) = get_thumbnail(rss_nails([entry.thumbnail]))
        if not name or not thumb:
            sys.stderr.write("Skipping, no thumbnail\n")
            continue

        item = BrochureItem(
            group  = src,
            title   = entry.title,
            desc    = entry.description,
            link    = entry.link,
            publish = entered,
            enabled = src.autoadd,
            indexed = indexed,
        )
        item.thumb.save(name[:255], thumb, save=True)

    src.publish = publish
    src.save()
    return "Done"

