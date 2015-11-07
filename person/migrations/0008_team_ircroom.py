# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0007_auto_20150830_1947'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='ircroom',
            field=models.CharField(max_length=64, null=True, verbose_name='IRC Chatroom Name', blank=True),
            preserve_default=True,
        ),
    ]
