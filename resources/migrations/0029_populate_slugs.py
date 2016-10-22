# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from resources.slugify import set_slug

def populate(apps, schema_editor):
    cls = apps.get_model("resources", "Category")
    for item in cls.objects.all():
        set_slug(item)
        item.save()

def depopulate(*args):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('resources', '0028_auto_20161022_1902'),
    ]

    operations = [
        migrations.RunPython(populate, depopulate),
    ]
