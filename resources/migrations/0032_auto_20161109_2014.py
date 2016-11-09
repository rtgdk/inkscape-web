# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0031_auto_20161030_0157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='extra_status',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(None, 'No extra status'), (1, 'Winner'), (2, 'Runner Up')]),
        ),
        migrations.AlterField(
            model_name='resource',
            name='thumbnail',
            field=pile.fields.ResizedImageField(format=b'PNG', upload_to=b'resources/thumb', max_width=780, min_height=190, max_height=600, blank=True, min_width=190, null=True, verbose_name='Thumbnail'),
        ),
    ]
