# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0005_auto_20161108_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useralertsetting',
            name='batch',
            field=models.CharField(choices=[(None, 'Instant'), (b'D', 'Daily'), (b'W', 'Weekly'), (b'M', 'Monthly')], max_length=1, blank=True, help_text='Save all alerts and send as one email, only affects email alerts.', null=True, verbose_name='Batch Alerts'),
        ),
        migrations.AlterField(
            model_name='useralertsetting',
            name='owner',
            field=models.BooleanField(default=True, help_text='Send the alert if it relates directly to me or my group.', verbose_name='Subscribe to Self'),
        ),
    ]
