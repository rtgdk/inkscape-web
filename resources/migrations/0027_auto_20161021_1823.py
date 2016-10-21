# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0026_auto_20161019_0334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='thumbnail',
            field=pile.fields.ResizedImageField(format=b'PNG', upload_to=b'resources/thumb', max_width=190, min_height=0, max_height=190, blank=True, min_width=0, null=True, verbose_name='Thumbnail'),
        ),
    ]
