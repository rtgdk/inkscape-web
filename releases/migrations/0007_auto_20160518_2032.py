# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0006_releasetranslation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='platform',
            name='matcher',
        ),
        migrations.RemoveField(
            model_name='releaseplatform',
            name='more_info',
        ),
        migrations.AddField(
            model_name='platform',
            name='match_bits',
            field=models.PositiveIntegerField(blank=True, null=True, db_index=True, choices=[(32, b'32bit'), (64, b'64bit')]),
        ),
        migrations.AddField(
            model_name='platform',
            name='match_family',
            field=models.CharField(help_text='User agent os match, whole string.', max_length=32, null=True, db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='platform',
            name='match_version',
            field=models.CharField(help_text='User agent os version partial match, e.g. |10|11| will match both version 10 and version 11, must have pipes at start and end of string.', max_length=32, null=True, db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='releaseplatform',
            name='info',
            field=models.TextField(null=True, verbose_name='Release Platform Information', blank=True),
        ),
        migrations.AlterField(
            model_name='release',
            name='background',
            field=pile.fields.ResizedImageField(format=b'PNG', upload_to=b'release/background', max_width=960, min_height=0, max_height=360, blank=True, min_width=0, null=True),
        ),
        migrations.AlterField(
            model_name='release',
            name='codename',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='Codename', blank=True),
        ),
        migrations.AlterField(
            model_name='release',
            name='release_date',
            field=models.DateField(db_index=True, null=True, verbose_name='Release date', blank=True),
        ),
        migrations.AlterField(
            model_name='release',
            name='version',
            field=models.CharField(unique=True, max_length=8, verbose_name='Version', db_index=True),
        ),
    ]
