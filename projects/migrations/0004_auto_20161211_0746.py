# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.utils.permissions
import pile.fields
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0003_auto_20160312_1649'),
    ]

    operations = [
        migrations.RenameField(
            model_name='criteria',
            old_name='detail',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='criteria',
            old_name='content',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='desc',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='sort',
            new_name='difficulty',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='delive',
            new_name='deliverable',
        ),
        migrations.RenameModel(
            old_name='ProjectUpdate',
            new_name='Report',
        ),
        migrations.RenameField(
            model_name='report',
            old_name='describe',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='relatedfile',
            name='for_update',
            field=models.ForeignKey(related_name='related_files', to='projects.Report'),
        ),
    ]
