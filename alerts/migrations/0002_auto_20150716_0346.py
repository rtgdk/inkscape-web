# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alerttype',
            name='private',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='alerttype',
            name='category',
            field=models.CharField(default=b'?', max_length=1, verbose_name='Category', choices=[(b'?', b'Unknown'), (b'U', b'User to User'), (b'S', b'System to User'), (b'A', b'Admin to User'), (b'P', b'User to Admin'), (b'T', b'System to Translator')]),
            preserve_default=True,
        ),
    ]
