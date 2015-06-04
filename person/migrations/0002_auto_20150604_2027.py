# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='enrole',
            field=models.CharField(default=b'O', max_length=1, verbose_name='Enrolement', choices=[(b'O', 'Open'), (b'P', 'Peer Invite'), (b'T', 'Admin Invite'), (b'C', 'Closed'), (b'S', 'Secret')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=32, verbose_name='Team Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='team',
            name='slug',
            field=models.SlugField(max_length=32, verbose_name='Team URL Slug'),
            preserve_default=True,
        ),
    ]
