# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.utils.permissions
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accusation', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(1024)])),
                ('flagged', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date Flagged', db_index=True)),
                ('flag', models.IntegerField(default=1, verbose_name='Flag Type', choices=[(1, 'Removal Suggestion'), (5, 'Moderator Approval'), (10, 'Moderator Deletion')])),
            ],
            options={
                'get_latest_by': 'flagged',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FlagCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('flag', models.IntegerField(default=1, verbose_name='Flag Type', choices=[(1, 'Removal Suggestion'), (5, 'Moderator Approval'), (10, 'Moderator Deletion')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='flag',
            name='category',
            field=models.ForeignKey(related_name='flags', blank=True, to='moderation.FlagCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flag',
            name='flagger',
            field=models.ForeignKey(related_name='flagged', default=cms.utils.permissions.get_current_user, verbose_name='Flagging User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flag',
            name='implicated',
            field=models.ForeignKey(related_name='flags_against', verbose_name='Implicated User', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
