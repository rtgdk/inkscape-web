# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0002_auto_20150517_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='end_contest',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='start_contest',
            field=models.DateField(help_text=b'If specified, this category will have special voting rules.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
