# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inkscape', '0002_auto_20160527_0115'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeartBeat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128, db_index=True)),
                ('status', models.IntegerField(default=0)),
                ('error', models.TextField()),
                ('beats', models.IntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
