# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0008_team_ircroom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='requests',
            field=models.ManyToManyField(related_name='team_requests', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='watchers',
            field=models.ManyToManyField(related_name='watches', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
