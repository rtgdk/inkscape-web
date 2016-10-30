# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0030_auto_20161022_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='contest_count',
            field=models.DateField(help_text='Voting is finished, but the votes are being counted.', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='extra_status',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(None, 'No extra status'), (1, 'Contest Winner'), (2, 'Contest Runner Up')]),
        ),
    ]
