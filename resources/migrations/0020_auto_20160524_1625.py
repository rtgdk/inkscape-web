# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resources', '0019_auto_20160524_1618'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resource',
            old_name='new_checked_sig',
            new_name='checked_sig',
        ),
        migrations.RenameField(
            model_name='resource',
            old_name='new_download',
            new_name='download',
        ),
        migrations.RenameField(
            model_name='resource',
            old_name='new_embed',
            new_name='embed',
        ),
        migrations.RenameField(
            model_name='resource',
            old_name='new_license',
            new_name='license',
        ),
        migrations.RenameField(
            model_name='resource',
            old_name='new_mirror',
            new_name='mirror',
        ),
        migrations.RenameField(
            model_name='resource',
            old_name='new_owner',
            new_name='owner',
        ),
        migrations.RenameField(
            model_name='resource',
            old_name='new_signature',
            new_name='signature',
        ),
        migrations.RenameField(
            model_name='resource',
            old_name='new_verified',
            new_name='verified',
        ),
        migrations.RenameField(
            model_name='resource',
            old_name='new_checked_by',
            new_name='checked_by'
        ),
    ]
