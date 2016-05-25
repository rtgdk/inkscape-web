# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moderation', '0002_commentflag_resourcefileflag_userflag'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ResourcefileFlag',
            new_name='ResourceFlag',
        ),
        migrations.AlterField(
            model_name='resourceflag',
            name='target',
            field=models.ForeignKey(related_name='moderation', to='resources.Resource'),
        ),
    ]
