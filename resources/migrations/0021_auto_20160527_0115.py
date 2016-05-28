# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0020_auto_20160524_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='checked_by',
            field=models.ForeignKey(related_name='resource_checks', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
