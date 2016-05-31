# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0022_auto_20160529_1919'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='category',
            name='icon',
            field=models.FileField(upload_to=b'category/icon', null=True, verbose_name='Category Icon (svg:128x128)', blank=True),
        ),
    ]
