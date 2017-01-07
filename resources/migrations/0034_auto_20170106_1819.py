# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0033_auto_20161112_0112'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='owner_name',
            field=models.CharField(max_length=128, null=True, verbose_name="Owner's Name", blank=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='extra_status',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(None, 'No extra status'), (1, 'Winner'), (2, 'Runner Up'), (3, 'Next Round')]),
        ),
    ]
