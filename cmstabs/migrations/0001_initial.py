# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pile.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0002_auto_20140816_1918'),
    ]

    operations = [
        migrations.CreateModel(
            name='InlinePage',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=64)),
            ],
            options={
                'db_table': 'extra_inlinepage',
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='InlinePages',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'db_table': 'extra_inlinepages',
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='ShieldPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'db_table': 'extra_shieldplugin',
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
                ('draft', models.ForeignKey(blank=True, to='cmstabs.Tab', null=True)),
                ('license', models.ForeignKey(to='resource.License')),
                ('shield', models.ForeignKey(related_name='tabs', to='cmstabs.ShieldPlugin')),
            ],
            options={
                'ordering': ('order',),
                'db_table': 'extra_tab',
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
                'db_table': 'extra_tabcategory',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tab',
            name='tab_cat',
            field=models.ForeignKey(verbose_name='Tab Icon', to='cmstabs.TabCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tab',
            name='user',
            field=models.ForeignKey(related_name='front_tabs', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
         migrations.CreateModel(
            name='GroupPhotoPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('style', models.CharField(max_length=1, verbose_name='Display Style', choices=[(b'L', 'Simple List'), (b'P', 'Photo Heads'), (b'B', 'Photo Bios')])),
                ('source', models.ForeignKey(to='auth.Group')),
            ],
            options={
                'abstract': False,
                'db_table': 'person_groupphotoplugin',
            },
            bases=('cms.cmsplugin',),
        ),
    ]
