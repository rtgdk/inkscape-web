# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0005_auto_20160212_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReleaseTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(help_text='Which language is this translated into.', max_length=8, verbose_name='Language', db_index=True, choices=[(b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'ja', b'Japanese'), (b'zh', b'Chinese'), (b'zh-hant', b'Simplified Chinese'), (b'ko', b'Korean')])),
                ('translated_notes', models.TextField(verbose_name='Release notes')),
                ('release', models.ForeignKey(related_name='translations', to='releases.Release')),
            ],
        ),
    ]
