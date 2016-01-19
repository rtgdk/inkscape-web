# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updatefile', models.FileField(upload_to=b'project/related_files', verbose_name='Related File')),
                ('for_update', models.ForeignKey(related_name='related_files', to='projects.ProjectUpdate')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='project',
            name='desc',
            field=models.TextField(blank=True, null=True, verbose_name='Description', validators=[django.core.validators.MaxLengthValidator(50192)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='duration',
            field=models.IntegerField(default=0, verbose_name='Expected Duration in Days'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='sort',
            field=models.IntegerField(default=2, verbose_name='Importance', choices=[(0, 'Wishlist'), (1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Critical')]),
            preserve_default=True,
        ),
    ]
