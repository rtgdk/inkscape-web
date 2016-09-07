# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_image', '0002_auto_20160907_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='title',
            field=models.CharField(help_text='When user hovers above picture, this text will appear in a popup.', max_length=255, null=True, verbose_name='Hover text', blank=True),
        ),
        migrations.AlterModelTable(
            name='image',
            table=None,
        ),
    ]
