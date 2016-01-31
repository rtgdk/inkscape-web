# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0003_auto_20150604_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='resources.Tag', null=True),
            preserve_default=True,
        ),
    ]
