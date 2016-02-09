# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0010_auto_20160206_0535'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamChatRoom',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('channel', models.CharField(max_length=64, verbose_name='IRC Chatroom Name')),
                ('language', models.CharField(default=b'en', max_length=5, choices=[(b'en', b'English'), (b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'ja', b'Japanese'), (b'zh', b'Chinese'), (b'zh-hant', b'Simplified Chinese'), (b'ko', b'Korean')])),
                ('admin', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='team',
            name='ircroom',
        ),
        migrations.AddField(
            model_name='teamchatroom',
            name='team',
            field=models.ForeignKey(related_name='ircrooms', to='person.Team'),
        ),
        migrations.AlterUniqueTogether(
            name='teamchatroom',
            unique_together=set([('language', 'team')]),
        ),
    ]
