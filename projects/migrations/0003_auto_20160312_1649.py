# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import pile.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20151225_0549'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updatefile', models.FileField(upload_to=b'project/related_files', verbose_name='Related File')),
                ('for_update', models.ForeignKey(related_name='related_files', to='projects.ProjectUpdate')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='desc',
            field=models.TextField(blank=True, null=True, verbose_name='Description', validators=[django.core.validators.MaxLengthValidator(50192)]),
        ),
        migrations.AddField(
            model_name='project',
            name='pitch',
            field=models.CharField(max_length=255, null=True, verbose_name='Short Summary', blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='banner',
            field=pile.fields.ResizedImageField(format=b'PNG', default=b'/static/images/project_banner.png', upload_to=b'project/banner', max_width=920, min_height=90, max_height=120, min_width=600, verbose_name='Banner (920x120)'),
        ),
        migrations.AlterField(
            model_name='project',
            name='duration',
            field=models.IntegerField(default=0, verbose_name='Expected Duration in Days'),
        ),
        migrations.AlterField(
            model_name='project',
            name='logo',
            field=pile.fields.ResizedImageField(format=b'PNG', default=b'/static/images/project_logo.png', upload_to=b'project/logo', max_width=150, min_height=150, max_height=150, min_width=150, verbose_name='Logo (150x150)'),
        ),
        migrations.AlterField(
            model_name='project',
            name='sort',
            field=models.IntegerField(default=2, verbose_name='Difficulty', choices=[(0, 'Unknown'), (1, 'Easy'), (2, 'Moderate'), (3, 'Hard'), (4, 'Very hard')]),
        ),
    ]
