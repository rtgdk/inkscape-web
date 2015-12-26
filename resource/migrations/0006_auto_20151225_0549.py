# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0005_auto_20151106_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='items',
            field=models.ManyToManyField(related_name='galleries', to='resource.Resource', blank=True),
        ),
        migrations.AlterField(
            model_name='quota',
            name='group',
            field=models.OneToOneField(related_name='quotas', null=True, blank=True, to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='tags',
            field=models.ManyToManyField(related_name='resources', to='resource.Tag', blank=True),
        ),
    ]
