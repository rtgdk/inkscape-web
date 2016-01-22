# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('cms', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPhotoPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('style', models.CharField(max_length=1, verbose_name='Display Style', choices=[(b'L', 'Simple List'), (b'P', 'Photo Heads'), (b'B', 'Photo Bios')])),
                ('source', models.ForeignKey(to='auth.Group')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='User Team')),
                ('icon', models.ImageField(upload_to=b'teams', verbose_name='Display Icon')),
                ('desc', models.TextField(blank=True, null=True, verbose_name='Full Description', validators=[django.core.validators.MaxLengthValidator(10240)])),
                ('group', pile.fields.AutoOneToOneField(related_name='team', null=True, blank=True, to='auth.Group')),
            ],
            options={
                'db_table': 'person_userroll',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bio', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(4096)])),
                ('photo', pile.fields.ResizedImageField(format=b'PNG', upload_to=b'photos', max_width=190, min_height=0, max_height=190, blank=True, min_width=0, null=True, verbose_name='Photograph (square)')),
                ('ircnick', models.CharField(max_length=20, null=True, verbose_name='IRC Nickname', blank=True)),
                ('ircpass', models.CharField(max_length=128, null=True, verbose_name='Freenode Password (optional)', blank=True)),
                ('ircdev', models.BooleanField(default=False, verbose_name='Join Developer Channel')),
                ('dauser', models.CharField(max_length=64, null=True, verbose_name='deviantArt User', blank=True)),
                ('ocuser', models.CharField(max_length=64, null=True, verbose_name='openClipArt User', blank=True)),
                ('tbruser', models.CharField(max_length=64, null=True, verbose_name='Tumblr User', blank=True)),
                ('gpg_key', models.TextField(blank=True, null=True, verbose_name='GPG Public Key', validators=[django.core.validators.MaxLengthValidator(262144)])),
                ('last_seen', models.DateTimeField(null=True, blank=True)),
                ('visits', models.IntegerField(default=0)),
                ('user', pile.fields.AutoOneToOneField(related_name='details', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
