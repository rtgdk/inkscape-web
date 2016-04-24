# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0013_resourcefile_embed'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('download', models.FileField(upload_to=b'resources/file', verbose_name='Consumable File')),
                ('signature', models.FileField(upload_to=b'resources/sigs', null=True, verbose_name='Signature/Checksum', blank=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('version', models.IntegerField(default=0)),
                ('resource', models.ForeignKey(related_name='revisions', to='resources.ResourceFile')),
            ],
        ),
        migrations.CreateModel(
            name='RevisionManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
    ]
