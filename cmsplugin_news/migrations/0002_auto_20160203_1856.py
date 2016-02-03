# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='language',
            field=models.CharField(help_text='Translated version of another news item.', max_length=5, verbose_name='Language', choices=[(b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'ja', b'Japanese'), (b'zh', b'Chinese'), (b'zh-hant', b'Simplified Chinese'), (b'ko', b'Korean')]),
        ),
    ]
