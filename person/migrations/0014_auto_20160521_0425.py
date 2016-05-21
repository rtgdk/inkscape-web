# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0013_auto_20160302_0515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='mailman',
            field=models.CharField(help_text=b'The name of the pre-configured mailing list for this team', max_length=32, null=True, verbose_name='Email List', blank=True),
        ),
    ]
