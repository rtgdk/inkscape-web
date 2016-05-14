# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort', models.IntegerField(default=0, null=True, blank=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('slug', models.SlugField(unique=True, max_length=128)),
                ('desc', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(1024)])),
                ('icon', models.FileField(null=True, upload_to=b'forum/icon', blank=True)),
                ('lang', models.CharField(help_text='Set this ONLY if you want this forum restricted to this language', max_length=8, null=True, blank=True)),
                ('last_posted', models.DateTimeField(db_index=True, null=True, verbose_name='Last Posted', blank=True)),
                ('content_type', models.ForeignKey(verbose_name='Fixed Content From', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('-sort',),
                'get_latest_by': 'last_posted',
            },
        ),
        migrations.CreateModel(
            name='ForumGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='ForumTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_pk', models.PositiveIntegerField(null=True, blank=True)),
                ('subject', models.CharField(max_length=128)),
                ('slug', models.SlugField(unique=True, max_length=128)),
                ('last_posted', models.DateTimeField(db_index=True, null=True, verbose_name='Last Posted', blank=True)),
                ('forum', models.ForeignKey(related_name='topics', to='forums.Forum')),
            ],
            options={
                'ordering': ('-last_posted',),
                'get_latest_by': 'last_posted',
            },
        ),
        migrations.AddField(
            model_name='forum',
            name='group',
            field=models.ForeignKey(related_name='forums', to='forums.ForumGroup'),
        ),
    ]
