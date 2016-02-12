# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0004_auto_20160126_2108'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='platform',
            options={'ordering': ('-order', 'codename')},
        ),
        migrations.AddField(
            model_name='platform',
            name='matcher',
            field=models.CharField(help_text='Autopick this platform if UserAgent matches this regular expression', max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='platform',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='release',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='releases.Release', null=True),
        ),
    ]
