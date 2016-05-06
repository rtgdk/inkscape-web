# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logbook', '0002_logfile_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='logmetric',
            name='icon',
            field=models.CharField(max_length=22, null=True, blank=True),
        ),
    ]
