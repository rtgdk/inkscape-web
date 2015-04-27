# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0011_auto_20150419_1006'),
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uri', models.CharField(max_length=255, db_index=True)),
                ('status', models.IntegerField(db_index=True)),
                ('count', models.IntegerField(default=0)),
                ('added', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InlinePage',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=64)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='InlinePages',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='ShieldPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Tab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('link', models.URLField(null=True, verbose_name='External Link', blank=True)),
                ('name', models.CharField(max_length=64)),
                ('download', models.FileField(upload_to=b'shields/backgrounds', verbose_name='Background')),
                ('order', models.IntegerField(null=True, blank=True)),
                ('tab_name', models.CharField(max_length=64, verbose_name='Heading')),
                ('tab_text', models.CharField(max_length=128, verbose_name='Sub-Heading')),
                ('banner_text', models.CharField(max_length=255, null=True, blank=True)),
                ('banner_foot', models.CharField(max_length=128, null=True, blank=True)),
                ('btn_text', models.CharField(max_length=32, null=True, verbose_name='Button Text', blank=True)),
                ('btn_link', models.CharField(max_length=255, null=True, verbose_name='Button Link', blank=True)),
                ('btn_icon', models.CharField(blank=True, max_length=12, null=True, verbose_name='Button Icon', choices=[(b'download', 'Download Icon')])),
                ('draft', models.ForeignKey(blank=True, to='extra.Tab', null=True)),
                ('license', models.ForeignKey(to='resource.License')),
                ('shield', models.ForeignKey(related_name='tabs', to='extra.ShieldPlugin')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TabCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=22)),
                ('icon', pile.fields.ResizedImageField(format=b'PNG', upload_to=b'shields/icons', max_height=32, min_height=0, max_width=32, min_width=0, verbose_name='Icon')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tab',
            name='tab_cat',
            field=models.ForeignKey(verbose_name='Tab Icon', to='extra.TabCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tab',
            name='user',
            field=models.ForeignKey(related_name='front_tabs', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
