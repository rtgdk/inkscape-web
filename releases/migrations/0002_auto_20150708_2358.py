# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='release',
            options={'ordering': ('-release_date',), 'get_latest_by': 'release_date'},
        ),
    ]
