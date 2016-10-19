# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('resources', '0024_auto_20161007_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='groups',
            field=models.ManyToManyField(help_text='The category is restricted to these groups only.', to='auth.Group', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='selectable',
            field=models.BooleanField(default=True, help_text='This category is not private/hidden from all users.'),
        ),
    ]
