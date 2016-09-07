# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.pluginmodel


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('cms', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=False, serialize=False, to='cms.CMSPlugin')),
                ('image', models.ImageField(upload_to=cms.models.pluginmodel.get_plugin_media_path, verbose_name='image', max_length=200)),
                ('url', models.CharField(help_text='If present, clicking on image will take user to link.', max_length=255, null=True, verbose_name='Link', blank=True)),
                ('page_link', models.ForeignKey(blank=True, to='cms.Page', help_text='If present, clicking on image will take user to specified cms page.', null=True, verbose_name='CMS page link')),
                ('alt', models.CharField(help_text='Specifies an alternate text for an image, if the imagecannot be displayed.<br />Is also used by search enginesto classify the image.', max_length=255, null=True, verbose_name='Alternate text', blank=True)),
                ('longdesc', models.CharField(help_text='When user hovers above picture, this text will appear in a popup.', max_length=255, null=True, verbose_name='long description', blank=True)),
                ('float', models.CharField(choices=[('left', 'left'), ('right', 'right'), ('center', 'center')], max_length=10, blank=True, help_text='Move image left, right or center.', null=True, verbose_name='side')),
                ('width', models.IntegerField(help_text='Width of the image in pixels. If set, image will be scaled proportionately.', null=True, verbose_name='width', blank=True)),
                ('height', models.IntegerField(help_text='Height of the image in pixels. If set together with width, image may be scaled disproportionately.', null=True, verbose_name='height', blank=True)),
            ],
            options={
                'db_table': 'djangocms_picture_picture',
            },
            bases=('cms.cmsplugin',),
        ),
    ]
