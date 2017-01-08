# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmstabs', '0002_add_inlinepages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tab',
            name='draft',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='cmstabs.Tab', null=True),
        ),
    ]
