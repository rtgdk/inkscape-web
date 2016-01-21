# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Views',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session', models.CharField(max_length=40)),
                ('resource', models.ForeignKey(related_name='views', to='resource.Resource')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='resource',
            name='slug',
            field=models.SlugField(max_length=70), 
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gallery',
            name='slug',
            field=models.SlugField(max_length=70), 
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='fullview',
            field=models.PositiveIntegerField(default=0, verbose_name='Full Views'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='license',
            name='nd',
            field=models.BooleanField(default=False, verbose_name='Non-Derivative'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='vote',
            name='vote',
        ),
    ]
