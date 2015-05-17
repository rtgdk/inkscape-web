# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='fullview',
            field=models.PositiveIntegerField(default=0, verbose_name='Full Views'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='license',
            name='nd',
            field=models.BooleanField(default=False, verbose_name='Non-Derivative'),
            preserve_default=True,
        ),
    ]
