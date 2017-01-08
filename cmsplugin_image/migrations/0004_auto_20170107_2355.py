# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_image', '0003_auto_20160907_2241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='alt',
            field=models.CharField(help_text='Specifies an alternate text for an image, if the image cannot be displayed (download error, browser for visually impaired people\u2026).<br />It is also used by web tools (e.g. search engines) to classify the image.', max_length=255, null=True, verbose_name='Alternate text', blank=True),
        ),
    ]
