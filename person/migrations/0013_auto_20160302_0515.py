# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0012_auto_20160221_0801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='enrole',
            field=models.CharField(default=b'O', max_length=1, verbose_name='Enrollment', choices=[(b'O', 'Open'), (b'P', 'Peer Approval'), (b'T', 'Admin Approval'), (b'C', 'Closed'), (b'S', 'Secret')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='gpg_key',
            field=models.TextField(blank=True, help_text='<strong>Signing and Checksums for Uploads</strong><br/> Either fill in a valid GPG key, so you can sign your uploads, or just enter any text to activate the upload validation feature which verifies your uploads by comparing checksums.<br/><strong>Usage in file upload/editing form:</strong><br/>If you have submitted a GPG key, you can upload a *.sig file, and your upload can be verified. You can also submit these checksum file types:<br/>*.md5, *.sha1, *.sha224, *.sha256, *.sha384 or *.sha512', null=True, verbose_name='GPG Public Key', validators=[django.core.validators.MaxLengthValidator(262144)]),
        ),
        migrations.AlterField(
            model_name='user',
            name='ocuser',
            field=models.CharField(max_length=64, null=True, verbose_name='Openclipart User', blank=True),
        ),
    ]
