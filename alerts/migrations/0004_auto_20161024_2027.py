# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0003_auto_20150827_0424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alerttype',
            name='slug',
            field=models.CharField(unique=True, max_length=32, verbose_name='URL Slug'),
        ),
    ]
