# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

FIELDS_MOVED = ['download', 'license', 'owner', 'signature', 'verified', 'mirror', 'embed', 'checked_by', 'checked_sig']

def move_to(apps, schema_editor):
    ResourceFile = apps.get_model("resources", "ResourceFile")
    # We would use ResourceFile.objects.update(**fields) but the resulting
    # sql is very very bad in django 1.8, printing every pk in the where clause.
    # fields is created using the F() prompt into a dictionary
    for item in ResourceFile.objects.all():
        for field in FIELDS_MOVED:
            setattr(item, 'new_' + field, getattr(item, field))
        item.save()

def move_comments(old_ct, new_ct):
    """Provide a generic function for moving comments in a migration"""
    def _inner(apps, schema_editor):
        ContentType = apps.get_model("contenttypes", "ContentType")
        try:
            Comment = apps.get_model("django_comments", "Comment")
            old = ContentType.objects.get(app_label=old_ct[0], model=old_ct[1]).pk
            new = ContentType.objects.get(app_label=new_ct[0], model=new_ct[1]).pk
        except:
            return
        Comment.objects.filter(content_type_id=old).update(content_type_id=new)
    return _inner

def rev(f, a, b):
    """Return two versions of a migration call with reversed arguments"""
    return (f(a,b), f(b,a))

def move_from(apps, schema_editor):
    ResourceFile = apps.get_model("resources", "ResourceFile")
    for item in ResourceFile.objects.all():
        for field in FIELDS_MOVED:
            setattr(item, field, getattr(item, 'new_' + field))
        item.save()

class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0017_auto_20160524_1551'),
    ]

    operations = [
        migrations.RunPython(move_to, move_from),
        migrations.RunPython(
            *rev(move_comments, ('resources', 'resourcefile'), ('resources', 'resource'))
        ),
    ]

