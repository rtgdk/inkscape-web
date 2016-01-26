# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0008_populate_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='created',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
