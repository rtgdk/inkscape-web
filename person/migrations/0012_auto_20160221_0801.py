# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0011_auto_20160208_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='charter',
            field=models.TextField(blank=True, null=True, verbose_name='Charter', validators=[django.core.validators.MaxLengthValidator(30240)]),
        ),
        migrations.AddField(
            model_name='team',
            name='side_bar',
            field=models.TextField(blank=True, null=True, verbose_name='Side Bar', validators=[django.core.validators.MaxLengthValidator(10240)]),
        ),
    ]
