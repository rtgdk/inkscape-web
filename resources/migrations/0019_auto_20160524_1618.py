# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0003_auto_20160524_1609'),
        ('resources', '0018_auto_20160524_1551'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resourcefile',
            name='checked_by',
        ),
        migrations.RemoveField(
            model_name='resourcefile',
            name='license',
        ),
        migrations.RemoveField(
            model_name='resourcefile',
            name='resource_ptr',
        ),
        migrations.DeleteModel(
            name='ResourceFile',
        ),
    ]
