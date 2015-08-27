# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0002_auto_20150716_0346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useralertobject',
            name='o_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
