# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0005_auto_20151106_2317'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='liked',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gallery',
            name='slug',
            field=models.CharField(max_length=70),
            preserve_default=True,
        ),
    ]
