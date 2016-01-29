# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from resource.slugify import set_slug

def populate(apps, schema_editor):
    for mod in ("Resource", "Gallery"):
        cls = apps.get_model("resource", mod)
        for item in cls.objects.all():
            set_slug(item)
            if hasattr(item, 'liked'):
                item.liked = item.votes.count()
            item.save()

def depopulate(*args):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('resource', '0007_auto_20160125_0523'),
    ]

    operations = [
        migrations.RunPython(populate, depopulate),
    ]
