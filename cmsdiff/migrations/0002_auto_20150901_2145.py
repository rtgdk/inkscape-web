# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reversion', '0002_auto_20141216_1509'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cmsdiff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='revisiondiff',
            name='comment',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='revisiondiff',
            name='revisions',
            field=models.ManyToManyField(related_name='diffs', null=True, to='reversion.Revision', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='revisiondiff',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='revisiondiff',
            name='revision',
            field=pile.fields.AutoOneToOneField(related_name='diff', null=True, blank=True, to='reversion.Revision'),
            preserve_default=True,
        ),
    ]
