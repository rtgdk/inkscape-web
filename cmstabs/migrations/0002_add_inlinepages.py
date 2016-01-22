# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cmstabs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InlinePage',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'extra_inlinepage',
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='InlinePages',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'db_table': 'extra_inlinepages',
            },
            bases=('cms.cmsplugin',),
        ),
    ]
