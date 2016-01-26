# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0002_auto_20150708_2358'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='platform',
            options={'ordering': ('desc',)},
        ),
        migrations.AddField(
            model_name='platform',
            name='codename',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='platform',
            name='icon',
            field=pile.fields.ResizedImageField(format=b'PNG', upload_to=b'release/icons', max_width=32, min_height=0, max_height=32, blank=True, min_width=0, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='platform',
            name='image',
            field=pile.fields.ResizedImageField(format=b'PNG', upload_to=b'release/icons', max_width=256, min_height=0, max_height=256, blank=True, min_width=0, null=True),
            preserve_default=True,
        ),
    ]
