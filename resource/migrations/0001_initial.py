# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields
import cms.utils.permissions
import django.utils.timezone
from django.conf import settings
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0011_auto_20150419_1006'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('desc', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(1024)])),
                ('visible', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('limit', models.PositiveIntegerField(verbose_name='Number of items per page')),
                ('display', models.CharField(blank=True, max_length=32, null=True, verbose_name='Display Style', choices=[(b'list', 'Gallery List'), (b'rows', 'Gallery Rows')])),
                ('source', models.ForeignKey(to='resource.Category')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('slug', models.CharField(max_length=70)),
                ('group', models.ForeignKey(related_name='galleries', blank=True, to='auth.Group', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GalleryPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('limit', models.PositiveIntegerField(verbose_name='Number of items per page')),
                ('display', models.CharField(blank=True, max_length=32, null=True, verbose_name='Display Style', choices=[(b'list', 'Gallery List'), (b'rows', 'Gallery Rows')])),
                ('source', models.ForeignKey(to='resource.Gallery')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('code', models.CharField(max_length=16)),
                ('link', models.URLField(null=True, blank=True)),
                ('banner', models.FileField(upload_to=b'license/banner', null=True, verbose_name='License Banner (svg:80x15)', blank=True)),
                ('icon', models.FileField(upload_to=b'license/icon', null=True, verbose_name='License Icon (svg:100x40)', blank=True)),
                ('at', models.BooleanField(default=True, verbose_name='Attribution')),
                ('sa', models.BooleanField(default=False, verbose_name='Copyleft (Share Alike)')),
                ('nc', models.BooleanField(default=False, verbose_name='Non-Commercial')),
                ('nd', models.BooleanField(default=False, verbose_name='Non-Derivitive')),
                ('visible', models.BooleanField(default=True)),
                ('replaced', models.ForeignKey(verbose_name='Replaced by', blank=True, to='resource.License', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('size', models.IntegerField(default=1024, verbose_name='Quota Size (KiB)')),
                ('group', models.ForeignKey(related_name='quotas', null=True, blank=True, to='auth.Group', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('slug', models.SlugField(max_length=70)),
                ('desc', models.TextField(blank=True, null=True, verbose_name='Description', validators=[django.core.validators.MaxLengthValidator(50192)])),
                ('created', models.DateTimeField(null=True, blank=True)),
                ('edited', models.DateTimeField(null=True, blank=True)),
                ('published', models.BooleanField(default=False)),
                ('thumbnail', pile.fields.ResizedImageField(format=b'PNG', upload_to=b'resources/thumb', max_width=190, min_height=0, max_height=190, blank=True, min_width=0, null=True, verbose_name='Thumbnail')),
                ('link', models.URLField(null=True, verbose_name='External Link', blank=True)),
                ('liked', models.PositiveIntegerField(default=0)),
                ('viewed', models.PositiveIntegerField(default=0)),
                ('downed', models.PositiveIntegerField(default=0, verbose_name='Downloaded')),
                ('media_type', models.CharField(max_length=64, null=True, verbose_name='File Type', blank=True)),
                ('media_x', models.IntegerField(null=True, blank=True)),
                ('media_y', models.IntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceFile',
            fields=[
                ('resource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='resource.Resource')),
                ('download', models.FileField(upload_to=b'resources/file', verbose_name='Consumable File')),
                ('owner', models.BooleanField(default=True, verbose_name='Permission', choices=[(None, 'No permission'), (True, 'I own the work'), (False, 'I have permission')])),
                ('signature', models.FileField(upload_to=b'resources/sigs', null=True, verbose_name='Signature/Checksum', blank=True)),
                ('verified', models.BooleanField(default=False)),
                ('mirror', models.BooleanField(default=False)),
                ('license', models.ForeignKey(blank=True, to='resource.License', null=True)),
            ],
            options={
            },
            bases=('resource.resource',),
        ),
        migrations.CreateModel(
            name='ResourceMirror',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=64, verbose_name='Unique Identifier')),
                ('name', models.CharField(max_length=64)),
                ('url', models.URLField(verbose_name='Full Base URL')),
                ('capacity', models.PositiveIntegerField(verbose_name='Capacity (MB/s)')),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('sync_time', models.DateTimeField(null=True, blank=True)),
                ('sync_count', models.PositiveIntegerField(default=0)),
                ('chk_time', models.DateTimeField(null=True, verbose_name='Check Time Date', blank=True)),
                ('chk_return', models.IntegerField(null=True, verbose_name='Check Returned HTTP Code', blank=True)),
                ('manager', models.ForeignKey(default=cms.utils.permissions.get_current_user, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=16)),
                ('parent', models.ForeignKey(blank=True, to='resource.Tag', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
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
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('resource', models.ForeignKey(related_name='votes', to='resource.Resource')),
                ('voter', models.ForeignKey(related_name='favorites', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='resource',
            name='category',
            field=models.ForeignKey(related_name='items', blank=True, to='resource.Category', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='tags',
            field=models.ManyToManyField(related_name='resources', null=True, to='resource.Tag', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='user',
            field=models.ForeignKey(related_name='resources', default=cms.utils.permissions.get_current_user, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gallery',
            name='items',
            field=models.ManyToManyField(related_name='galleries', null=True, to='resource.Resource', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gallery',
            name='user',
            field=models.ForeignKey(related_name='galleries', default=cms.utils.permissions.get_current_user, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='acceptable_licenses',
            field=models.ManyToManyField(to='resource.License'),
            preserve_default=True,
        ),
    ]
