# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.pluginmodel


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('cmstabs', '0002_add_inlinepages'),
    ]

    operations = [
        migrations.CreateModel(
            name='InkPicture',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('image', models.FileField(upload_to=cms.models.pluginmodel.get_plugin_media_path, verbose_name='Image File')),
                ('url', models.CharField(help_text='If present, clicking on image will take user to link.', max_length=255, null=True, verbose_name='Link', blank=True)),
                ('alt', models.CharField(help_text='Specifies an alternate text for an image, if the imagecannot be displayed.<br />Is also used by search enginesto classify the image.', max_length=255, null=True, verbose_name='Alternate text', blank=True)),
                ('title', models.CharField(help_text='When user hovers above picture, this text will appear in a popup.', max_length=255, null=True, verbose_name='Hover text', blank=True)),
                ('caption', models.CharField(help_text='If set, the image will be nested into a figure tag together with this caption.', max_length=512, null=True, verbose_name='Image caption', blank=True)),
                ('float', models.CharField(choices=[(b'left', 'left'), (b'right', 'right'), (b'center', 'center')], max_length=10, blank=True, help_text='Move image left, right or center.', null=True, verbose_name='side')),
                ('width', models.IntegerField(help_text='Width of the image in pixels. If set, image will be scaled proportionately.', null=True, verbose_name='width', blank=True)),
                ('extra_styling', models.CharField(help_text="Additional styles to apply to the figure or img element, e.g. 'margin-top: 0.5em; border: 1px solid grey;'. Be careful to not break the layout!", max_length=255, null=True, verbose_name='Extra styles', blank=True)),
                ('page_link', models.ForeignKey(blank=True, to='cms.Page', help_text='If present, clicking on image will take user to specified cms page.', null=True, verbose_name='CMS page link')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
