# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0004_auto_20161024_2027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alerttype',
            name='category',
        ),
        migrations.RemoveField(
            model_name='alerttype',
            name='default_hide',
        ),
        migrations.RemoveField(
            model_name='alerttype',
            name='private',
        ),
        migrations.RemoveField(
            model_name='useralertsetting',
            name='hide',
        ),
        migrations.AddField(
            model_name='alerttype',
            name='default_batch',
            field=models.CharField(blank=True, max_length=1, null=True, choices=[(None, 'Instant'), (b'D', 'Daily'), (b'W', 'Weekly'), (b'M', 'Monthly')]),
        ),
        migrations.AddField(
            model_name='alerttype',
            name='default_irc',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='useralertsetting',
            name='batch',
            field=models.CharField(choices=[(None, 'Instant'), (b'D', 'Daily'), (b'W', 'Weekly'), (b'M', 'Monthly')], max_length=1, blank=True, help_text='Save all alerts and send as one email, only effects email alerts.', null=True, verbose_name='Batch Alerts'),
        ),
        migrations.AddField(
            model_name='useralertsetting',
            name='irc',
            field=models.BooleanField(default=False, help_text='If online, this alert will be sent to my irc nickname.', verbose_name='Send IRC Alert'),
        ),
        migrations.AddField(
            model_name='useralertsetting',
            name='owner',
            field=models.BooleanField(default=True, help_text='Send the alert if it sent directly to me or my group.', verbose_name='Direct Messages'),
        ),
        migrations.AlterField(
            model_name='useralertsetting',
            name='email',
            field=models.BooleanField(default=False, help_text='Send the alert to the account email address.', verbose_name='Send Email Alert'),
        ),
    ]
