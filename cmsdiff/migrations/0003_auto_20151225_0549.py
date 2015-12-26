# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsdiff', '0002_auto_20150901_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='revisiondiff',
            name='revisions',
            field=models.ManyToManyField(related_name='diffs', to='reversion.Revision', blank=True),
        ),
    ]
