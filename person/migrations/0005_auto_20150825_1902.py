# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('person', '0004_auto_20150708_2117'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='members',
            new_name='group',
        ),
        migrations.AddField(
            model_name='team',
            name='requests',
            field=models.ManyToManyField(related_name='team_requests', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
    ]
