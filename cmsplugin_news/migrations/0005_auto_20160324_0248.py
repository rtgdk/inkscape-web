# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_news', '0004_auto_20160321_1954'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ('-pub_date',), 'verbose_name': 'News', 'verbose_name_plural': 'News', 'permissions': (('translate_news', 'Translate News'),)},
        ),
        migrations.AlterField(
            model_name='news',
            name='slug',
            field=models.SlugField(unique_for_date=b'pub_date', help_text='A slug is a short name which provides a unique url.', null=True, verbose_name='Slug'),
        ),
    ]
