# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0034_auto_20170106_1819'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='views',
            name='resource',
        ),
        migrations.DeleteModel(
            name='Views',
        ),
    ]
