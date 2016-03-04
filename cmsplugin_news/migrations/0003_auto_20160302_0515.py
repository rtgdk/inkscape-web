# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_news', '0002_auto_20160203_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='link',
            field=models.URLField(help_text='This link will be used as absolute url for this item and replaces the view logic. <br />Note that by default this only applies for items with an empty "content" field.', null=True, verbose_name='Link', blank=True),
        ),
    ]
