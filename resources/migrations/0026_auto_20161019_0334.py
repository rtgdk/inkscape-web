# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0025_auto_20161019_0315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='media_type',
            field=models.CharField(max_length=128, null=True, verbose_name='File Type', blank=True),
        ),
    ]
