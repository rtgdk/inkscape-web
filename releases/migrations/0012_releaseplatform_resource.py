# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0036_auto_20170316_1158'),
        ('releases', '0011_auto_20170216_2346'),
    ]

    operations = [
        migrations.AddField(
            model_name='releaseplatform',
            name='resource',
            field=models.ForeignKey(blank=True, to='resources.Resource', null=True),
        ),
    ]
