# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators
import pile.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('person', '0002_rename_team_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_user', models.ForeignKey(related_name='friends', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='from_friends', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='userdetails',
            options={'permissions': [('website_cla_agreed', 'Agree to Website License')]},
        ),
        migrations.AddField(
            model_name='team',
            name='admin',
            field=models.ForeignKey(related_name='admin_teams', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='team',
            name='enrole',
            field=models.CharField(default=b'O', max_length=1, verbose_name='Enrolement', choices=[(b'O', 'Open'), (b'P', 'Peer Approval'), (b'T', 'Admin Approval'), (b'C', 'Closed'), (b'S', 'Secret')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='team',
            name='intro',
            field=models.TextField(blank=True, null=True, verbose_name='Introduction', validators=[django.core.validators.MaxLengthValidator(1024)]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='team',
            name='ircroom',
            field=models.CharField(max_length=64, null=True, verbose_name='IRC Chatroom Name', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='team',
            name='mailman',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='team',
            name='requests',
            field=models.ManyToManyField(related_name='team_requests', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='team',
            name='slug',
            field=models.SlugField(default='NONE', max_length=32, verbose_name='Team URL Slug'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='watchers',
            field=models.ManyToManyField(related_name='watches', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userdetails',
            name='language',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='Default Language', choices=[(b'en', b'English'), (b'de', b'German'), (b'da', b'Danish'), (b'fr', b'French'), (b'nl', b'Dutch'), (b'it', b'Italian'), (b'es', b'Spanish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'cs', b'Czech'), (b'ru', b'Russian'), (b'ja', b'Japanese'), (b'zh', b'Chinese'), (b'zh-tw', b'Simplified Chinese'), (b'ko', b'Korean')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='team',
            name='group',
            field=pile.fields.AutoOneToOneField(related_name='team', default=1, to='auth.Group'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='team',
            name='icon',
            field=models.ImageField(default=b'/static/images/team.svg', upload_to=b'teams', verbose_name='Display Icon'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=32, verbose_name='Team Name'),
            preserve_default=True,
        ),
    ]
