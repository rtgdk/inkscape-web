# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings

def is_test_db():
    return settings.DATABASES.get('default', {})\
            .get('NAME', '').startswith('test_')


class Migration(migrations.Migration):
    dependencies = [
        ('forums', '0001_initial'),
    ]

    if is_test_db():
        operations = [
            migrations.CreateModel(
                name='TestObject',
                fields=[
                    ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                    ('name', models.CharField(max_length=32)),
                ],
            ),
        ]

