# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resources', '0001_initial'),
        ('django_comments', '__first__'),
        ('moderation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentFlag',
            fields=[
                ('flag_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='moderation.Flag')),
                ('target', models.ForeignKey(related_name='moderation', to='django_comments.Comment')),
            ],
            options={
            },
            bases=('moderation.flag',),
        ),
        migrations.CreateModel(
            name='ResourcefileFlag',
            fields=[
                ('flag_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='moderation.Flag')),
                ('target', models.ForeignKey(related_name='moderation', to='resources.ResourceFile')),
            ],
            options={
            },
            bases=('moderation.flag',),
        ),
        migrations.CreateModel(
            name='UserFlag',
            fields=[
                ('flag_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='moderation.Flag')),
                ('target', models.ForeignKey(related_name='moderation', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=('moderation.flag',),
        ),
    ]
