# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('desc', models.CharField(max_length=255, verbose_name='Description')),
                ('icon', pile.fields.ResizedImageField(format=b'PNG', upload_to=b'release/icons', max_width=32, min_height=0, max_height=32, blank=True, min_width=0, null=True, verbose_name='Icon (32x32)')),
                ('image', pile.fields.ResizedImageField(format=b'PNG', upload_to=b'release/icons', max_width=256, min_height=0, max_height=256, blank=True, min_width=0, null=True, verbose_name='Logo (256x256)')),
                ('manager', models.ForeignKey(verbose_name='Platform Manager', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', models.ForeignKey(related_name='children', verbose_name='Parent Platform', blank=True, to='releases.Platform', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(unique=True, max_length=8, verbose_name='Version')),
                ('codename', models.CharField(max_length=32, null=True, verbose_name='Codename', blank=True)),
                ('release_notes', models.TextField(null=True, verbose_name='Release notes', blank=True)),
                ('release_date', models.DateField(null=True, verbose_name='Release date', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Date created', db_index=True)),
                ('edited', models.DateTimeField(auto_now=True, verbose_name='Last edited')),
                ('manager', models.ForeignKey(related_name='manages_releases', verbose_name='Release Manager', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('reviewer', models.ForeignKey(related_name='reviews_releases', verbose_name='Release Reviewer', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-version',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleasePlatform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('download', models.URLField(null=True, verbose_name='Download Link', blank=True)),
                ('more_info', models.URLField(null=True, verbose_name='More Info Link', blank=True)),
                ('howto', models.URLField(null=True, verbose_name='Instructions Link', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Date created', db_index=True)),
                ('platform', models.ForeignKey(related_name='releases', verbose_name='Release Platform', to='releases.Platform')),
                ('release', models.ForeignKey(related_name='platforms', verbose_name='Release', to='releases.Release')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
