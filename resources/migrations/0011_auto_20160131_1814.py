# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0010_auto_20160130_0259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='items',
            field=models.ManyToManyField(related_name='galleries', null=True, to='resources.Resource', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='resource',
            name='tags',
            field=models.ManyToManyField(related_name='resources', null=True, to='resources.Tag', blank=True),
            preserve_default=True,
        ),
        migrations.AlterModelTable(
            name='category',
            table=None,
        ),
        migrations.AlterModelTable(
            name='categoryplugin',
            table=None,
        ),
        migrations.AlterModelTable(
            name='gallery',
            table=None,
        ),
        migrations.AlterModelTable(
            name='galleryplugin',
            table=None,
        ),
        migrations.AlterModelTable(
            name='quota',
            table=None,
        ),
        migrations.AlterModelTable(
            name='resource',
            table=None,
        ),
        migrations.AlterModelTable(
            name='resourcefile',
            table=None,
        ),
        migrations.AlterModelTable(
            name='resourcemirror',
            table=None,
        ),
        migrations.AlterModelTable(
            name='tag',
            table=None,
        ),
        migrations.AlterModelTable(
            name='views',
            table=None,
        ),
        migrations.AlterModelTable(
            name='vote',
            table=None,
        ),
    ]
