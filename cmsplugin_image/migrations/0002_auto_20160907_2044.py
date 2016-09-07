# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.models.pluginmodel


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_image', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='caption',
            field=models.CharField(help_text='If set, the image will be nested into a figure tag together with this caption.', max_length=512, null=True, verbose_name='Image caption', blank=True),
        ),
        migrations.AddField(
            model_name='image',
            name='extra_styling',
            field=models.CharField(help_text="Additional styles to apply to the figure or img element, e.g. 'margin-top: 0.5em; border: 1px solid grey;'. Be careful to not break the layout!", max_length=255, null=True, verbose_name='Extra styles', blank=True),
        ),
        migrations.RenameField(
            model_name='image',
            old_name='longdesc',
            new_name='title',
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.FileField(upload_to=cms.models.pluginmodel.get_plugin_media_path, verbose_name='Image File'),
        ),
    ]
