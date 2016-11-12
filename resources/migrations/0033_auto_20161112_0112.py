# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0032_auto_20161109_2014'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='rendering',
            field=pile.fields.ResizedImageField(format=b'PNG', upload_to=b'resources/render', max_width=780, min_height=0, max_height=600, blank=True, min_width=0, null=True, verbose_name='Rendering'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='thumbnail',
            field=pile.fields.ResizedImageField(format=b'PNG', upload_to=b'resources/thumb', max_width=190, min_height=0, max_height=190, blank=True, min_width=0, null=True, verbose_name='Thumbnail'),
        ),
    ]
