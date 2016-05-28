# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('releases', '0007_auto_20160518_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='bug_manager',
            field=models.ForeignKey(related_name='bug_releases', blank=True, to=settings.AUTH_USER_MODEL, help_text='Manages critical bugs and decides what needs fixing.', null=True),
        ),
        migrations.AddField(
            model_name='release',
            name='translation_manager',
            field=models.ForeignKey(related_name='tr_releases', blank=True, to=settings.AUTH_USER_MODEL, help_text='Translation managers look after all translations for the release.', null=True),
        ),
        migrations.AlterField(
            model_name='release',
            name='manager',
            field=models.ForeignKey(related_name='releases', blank=True, to=settings.AUTH_USER_MODEL, help_text='Looks after the release schedule and release meetings.', null=True),
        ),
        migrations.AlterField(
            model_name='release',
            name='reviewer',
            field=models.ForeignKey(related_name='rev_releases', blank=True, to=settings.AUTH_USER_MODEL, help_text='Reviewers help to make sure the release is working.', null=True),
        ),
    ]
