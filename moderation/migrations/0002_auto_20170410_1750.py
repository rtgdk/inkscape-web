# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flagobject',
            name='object_owner',
            field=models.ForeignKey(related_name='flagged', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Owning User', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
