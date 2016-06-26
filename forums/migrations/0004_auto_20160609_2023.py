# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forums', '0003_auto_20160608_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumtopic',
            name='locked',
            field=models.BooleanField(default=False, help_text='Topic is locked by moderator.'),
        ),
        migrations.AlterField(
            model_name='forumtopic',
            name='sticky',
            field=models.IntegerField(default=0, help_text='If set, will stick this post to the top of the topics list. Higher numbers appear nearer the top. Same numbers will appear together, sorted by date.', verbose_name='Sticky Priority'),
        ),
    ]
