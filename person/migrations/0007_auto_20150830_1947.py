# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0006_auto_20150828_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdetails',
            name='language',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='Default Language', choices=[(b'en', b'English'), (b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'ja', b'Japanese'), (b'zh', b'Chinese'), (b'zh-tw', b'Simplified Chinese'), (b'ko', b'Korean')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='team',
            name='enrole',
            field=models.CharField(default=b'O', max_length=1, verbose_name='Enrolement', choices=[(b'O', 'Open'), (b'P', 'Peer Approval'), (b'T', 'Admin Approval'), (b'C', 'Closed'), (b'S', 'Secret')]),
            preserve_default=True,
        ),
    ]
