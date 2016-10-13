# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0023_auto_20160531_1835'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='end_contest',
        ),
        migrations.RemoveField(
            model_name='category',
            name='start_contest',
        ),
        migrations.AddField(
            model_name='category',
            name='acceptable_media_x',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='acceptable_media_y',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='acceptable_size',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='acceptable_types',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='gallery',
            name='category',
            field=models.ForeignKey(related_name='galleries', blank=True, to='resources.Category', null=True),
        ),
        migrations.AddField(
            model_name='gallery',
            name='contest_finish',
            field=models.DateField(help_text='Finish the contest, voting closed, winner announced (UTC).', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='gallery',
            name='contest_submit',
            field=models.DateField(help_text='Start a contest in this gallery on this date (UTC).', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='gallery',
            name='contest_voting',
            field=models.DateField(help_text='Finish the submissions and start voting (UTC).', null=True, blank=True),
        ),
    ]
