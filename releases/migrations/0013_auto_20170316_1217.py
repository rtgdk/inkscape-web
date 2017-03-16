# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def link_resource(apps, schema_editor):
    """Switch to having an optional resource link"""
    ReleasePlatform = apps.get_model("releases", "ReleasePlatform")
    Resource = apps.get_model("resources", "Resource")
    for rp in ReleasePlatform.objects.all():
        if rp.download is None or '/gallery/item/' not in rp.download:
            continue
        # https://inkscape.org/en/gallery/item/8841/inkscape-debuginfo-0.40-0.fdr.3.i386.rpm
        (_, last) = rp.download.split('/gallery/item/')
        (pk, _) = last.split('/', 1)
        try:
            r = Resource.objects.get(pk=pk)
            rp.download = None
            rp.resource = r
            rp.save()
        except Resource.DoesNotExist:
            continue


def delink_resource(*args):
    """Backwards move back to using download links"""
    ReleasePlatform = apps.get_model("releases", "ReleasePlatform")
    for rp in ReleasePlatform.objects.all():
        if rp.resource is None:
            continue
        rp.download = rp.resource.get_absolute_url()
        rp.resource = None
        rp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0012_releaseplatform_resource'),
    ]

    operations = [
        migrations.RunPython(link_resource, delink_resource),
    ]
