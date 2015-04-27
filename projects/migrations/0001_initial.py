# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields
import cms.utils.permissions
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Criteria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=255, verbose_name='Criteria')),
                ('detail', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(4096)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Deliverable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Deliverable')),
                ('sort', models.IntegerField(default=0)),
                ('targeted', models.DateField(null=True, blank=True)),
                ('finished', models.DateField(null=True, blank=True)),
            ],
            options={
                'ordering': ('sort',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort', models.IntegerField(verbose_name='Importance')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('slug', models.SlugField(unique=True)),
                ('banner', pile.fields.ResizedImageField(format=b'PNG', upload_to=b'project/banner', max_height=120, min_height=90, max_width=920, min_width=600, verbose_name='Banner (120x920)')),
                ('logo', pile.fields.ResizedImageField(format=b'PNG', upload_to=b'project/logo', max_height=150, min_height=150, max_width=150, min_width=150, verbose_name='Logo (150x150)')),
                ('duration', models.IntegerField(verbose_name='Expected Duration in Days')),
                ('started', models.DateTimeField(null=True, blank=True)),
                ('finished', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('is_fundable', models.BooleanField(default=False)),
                ('is_approved', models.BooleanField(default=False, verbose_name='Pre-approved')),
                ('criteria', models.ManyToManyField(to='projects.Criteria', null=True, blank=True)),
                ('manager', models.ForeignKey(related_name='manages_projects', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=128, verbose_name='Type Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('describe', models.TextField(verbose_name='Description', validators=[django.core.validators.MaxLengthValidator(12288)])),
                ('image', pile.fields.ResizedImageField(format=b'PNG', upload_to=b'project/update/%Y', max_width=400, min_height=0, max_height=400, blank=True, min_width=0, null=True, verbose_name='Image')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('edited', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(default=cms.utils.permissions.get_current_user, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(related_name='updates', to='projects.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Task')),
                ('targeted', models.DateField(null=True, blank=True)),
                ('finished', models.DateField(null=True, blank=True)),
                ('delive', models.ForeignKey(related_name='tasks', to='projects.Deliverable')),
            ],
            options={
                'ordering': ('targeted',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('plan', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(8192)])),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('vetted', models.DateTimeField(null=True, blank=True)),
                ('assigned', models.BooleanField(default=False)),
                ('project', models.ForeignKey(related_name='workers', to='projects.Project')),
                ('user', models.ForeignKey(related_name='works', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='project',
            name='project_type',
            field=models.ForeignKey(to='projects.ProjectType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='proposer',
            field=models.ForeignKey(related_name='proposed_projects', default=cms.utils.permissions.get_current_user, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='reviewer',
            field=models.ForeignKey(related_name='reviews_projects', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='second',
            field=models.ForeignKey(related_name='seconds_projects', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deliverable',
            name='project',
            field=models.ForeignKey(related_name='deliverables', to='projects.Project'),
            preserve_default=True,
        ),
    ]
