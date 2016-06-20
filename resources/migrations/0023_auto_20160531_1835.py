# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0022_auto_20160529_1919'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='category',
            name='symbol',
            field=models.FileField(upload_to=b'category/icon', null=True, verbose_name='Category Icon (svg:128x128)', blank=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='category',
            field=models.ForeignKey(related_name='items', verbose_name='Category', blank=True, to='resources.Category', null=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='license',
            field=models.ForeignKey(verbose_name='License', blank=True, to='resources.License', null=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='tags',
            field=models.ManyToManyField(related_name='resources', verbose_name='Tags', to='resources.Tag', blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(unique=True, max_length=16),
        ),
    ]
