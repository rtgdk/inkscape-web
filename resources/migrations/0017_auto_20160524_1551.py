# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resources', '0016_auto_20160512_0226'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='new_checked_sig',
            field=models.FileField(upload_to=b'resources/sigs', null=True, verbose_name='Counter Signature', blank=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='new_checked_by',
            field=models.ForeignKey(related_name='new_resource_checks', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='new_download',
            field=models.FileField(upload_to=b'resources/file', null=True, verbose_name='Consumable File', blank=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='new_embed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='resource',
            name='new_license',
            field=models.ForeignKey(blank=True, to='resources.License', null=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='new_mirror',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='resource',
            name='new_owner',
            field=models.BooleanField(default=True, verbose_name='Permission', choices=[(None, 'No permission'), (True, 'I own the work'), (False, 'I have permission')]),
        ),
        migrations.AddField(
            model_name='resource',
            name='new_signature',
            field=models.FileField(upload_to=b'resources/sigs', null=True, verbose_name='Signature/Checksum', blank=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='new_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='resourcerevision',
            name='resource',
            field=models.ForeignKey(related_name='revisions', to='resources.Resource'),
        ),
        migrations.AlterField(
            model_name='tagcategory',
            name='categories',
            field=models.ManyToManyField(help_text='Only show with these categories', related_name='tags', to='resources.Category'),
        ),
    ]
