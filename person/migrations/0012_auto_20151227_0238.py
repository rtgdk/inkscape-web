# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0011_auto_20151227_0224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdetails',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserDetails',
        ),
    ]
