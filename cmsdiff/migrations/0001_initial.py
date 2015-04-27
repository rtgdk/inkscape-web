# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('reversion', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='RevisionDiff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('stub', models.TextField(null=True, blank=True)),
                ('revision', pile.fields.AutoOneToOneField(related_name='diff', to='reversion.Revision')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
