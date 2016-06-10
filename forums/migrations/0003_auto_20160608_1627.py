# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forums', '0002_auto_20160514_0737'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='forumtopic',
            options={'ordering': ('-sticky', '-last_posted'), 'get_latest_by': 'last_posted'},
        ),
        migrations.AddField(
            model_name='forumtopic',
            name='sticky',
            field=models.IntegerField(default=0, verbose_name='If set, this post will be this sticky'),
        ),
    ]
