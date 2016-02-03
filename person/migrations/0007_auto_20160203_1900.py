# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0006_auto_20160203_0421'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='ircdev',
        ),
        migrations.AlterField(
            model_name='user',
            name='gpg_key',
            field=models.TextField(blank=True, help_text='\n          <strong>Signing and Checksums for Uploads</strong><br/>\n          Either fill in a valid GPG key, so you can sign your uploads, or just enter any text to activate the upload validation feature which verifies your uploads by comparing checksums." %}<br/>\n          <strong>Usage in file upload/editing form:</strong><br/>\n          If you have submitted a GPG key, you can upload a *.sig file, and your upload can be verified. You can also submit these checksum file types:" %}<br/>\n          *.md5, *.sha1, *.sha224, *.sha256, *.sha384 {% trans "or" %} *.sha512\n        ', null=True, verbose_name='GPG Public Key', validators=[django.core.validators.MaxLengthValidator(262144)]),
        ),
        migrations.AlterField(
            model_name='user',
            name='language',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='Default Language', choices=[(b'en', b'English'), (b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'ja', b'Japanese'), (b'zh', b'Chinese'), (b'zh-hant', b'Simplified Chinese'), (b'ko', b'Korean')]),
        ),
    ]
