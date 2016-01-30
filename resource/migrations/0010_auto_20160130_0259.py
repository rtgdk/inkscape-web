# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0009_auto_20160126_1052'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='visible',
            new_name='selectable',
        ),
        migrations.RenameField(
            model_name='license',
            old_name='visible',
            new_name='selectable',
        ),
        migrations.AddField(
            model_name='category',
            name='filterable',
            field=models.BooleanField(default=True, help_text='This category can be used as a filter in gallery indexes.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='license',
            name='filterable',
            field=models.BooleanField(default=True, help_text='This license can be used as a filter in gallery indexes.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='category',
            name='selectable',
            field=models.BooleanField(default=True, help_text='This category can be selected by all users when uploading.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='license',
            name='selectable',
            field=models.BooleanField(default=True, help_text='This license can be selected by all users when uploading.'),
            preserve_default=True,
        ),
    ]
