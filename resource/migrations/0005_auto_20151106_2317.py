# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0004_auto_20150828_1602'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resource',
            options={'get_latest_by': 'created'},
        ),
    ]
