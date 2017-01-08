# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0014_auto_20160521_0425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teamchatroom',
            name='language',
            field=models.CharField(default=b'en', max_length=5, choices=[(b'ar', b'Arabic'), (b'en', b'English'), (b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'ja', b'Japanese'), (b'zh', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'ko', b'Korean')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, null=True, verbose_name='Bio', validators=[django.core.validators.MaxLengthValidator(4096)]),
        ),
        migrations.AlterField(
            model_name='user',
            name='language',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='Default Language', choices=[(b'ar', b'Arabic'), (b'en', b'English'), (b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'ja', b'Japanese'), (b'zh', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'ko', b'Korean')]),
        ),
    ]
