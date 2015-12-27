# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import django.contrib.auth.models
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0009_auto_20151225_0549'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(4096)]),
        ),
        migrations.AddField(
            model_name='user',
            name='dauser',
            field=models.CharField(max_length=64, null=True, verbose_name='deviantArt User', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='gpg_key',
            field=models.TextField(blank=True, null=True, verbose_name='GPG Public Key', validators=[django.core.validators.MaxLengthValidator(262144)]),
        ),
        migrations.AddField(
            model_name='user',
            name='ircdev',
            field=models.BooleanField(default=False, verbose_name='Join Developer Channel'),
        ),
        migrations.AddField(
            model_name='user',
            name='ircnick',
            field=models.CharField(max_length=20, null=True, verbose_name='IRC Nickname', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='ircpass',
            field=models.CharField(max_length=128, null=True, verbose_name='Freenode Password (optional)', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='Default Language', choices=[(b'en', b'English'), (b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'ja', b'Japanese'), (b'zh', b'Chinese'), (b'zh-tw', b'Simplified Chinese'), (b'ko', b'Korean')]),
        ),
        migrations.AddField(
            model_name='user',
            name='last_seen',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='ocuser',
            field=models.CharField(max_length=64, null=True, verbose_name='openClipArt User', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='photo',
            field=pile.fields.ResizedImageField(format=b'PNG', upload_to=b'photos', max_width=190, min_height=0, max_height=190, blank=True, min_width=0, null=True, verbose_name='Photograph (square)'),
        ),
        migrations.AddField(
            model_name='user',
            name='tbruser',
            field=models.CharField(max_length=64, null=True, verbose_name='Tumblr User', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='visits',
            field=models.IntegerField(default=0),
        ),
    ]
