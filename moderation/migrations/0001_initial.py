# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FlagObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('resolution', models.NullBooleanField(default=None, choices=[(None, 'Pending Moderator Action'), (True, 'Object is Retained'), (False, 'Object is Deleted')])),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('object_owner', models.ForeignKey(related_name='flagged', verbose_name='Owning User', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FlagVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date Flagged', db_index=True)),
                ('weight', models.IntegerField(default=1)),
                ('notes', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(1024)])),
                ('moderator', models.ForeignKey(related_name='flags', to=settings.AUTH_USER_MODEL)),
                ('target', models.ForeignKey(related_name='votes', to='moderation.FlagObject')),
            ],
            options={
                'get_latest_by': 'created',
                'permissions': (('can_moderate', 'User can moderate flagged content.'),),
            },
        ),
    ]
