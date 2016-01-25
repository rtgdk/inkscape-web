# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0006_auto_20160123_0517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='slug',
            field=models.SlugField(max_length=70),
            preserve_default=True,
        ),
    ]
