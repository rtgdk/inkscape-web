# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '0002_update_user_email_field_length'),
        ('forums', '0004_auto_20160609_2023'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_id', models.CharField(help_text=b'A unique identifier for this message', unique=True, max_length=255, db_index=True)),
                ('reply_id', models.CharField(help_text=b'Either the previous message in the chain, or the parent id', max_length=255, null=True, db_index=True, blank=True)),
                ('subject', models.CharField(help_text=b'A matchable subject line for this comment.', max_length=255, null=True, db_index=True, blank=True)),
                ('extra_data', models.TextField(null=True, blank=True)),
                ('comment', models.OneToOneField(related_name='link', to='django_comments.Comment')),
            ],
        ),
        migrations.AddField(
            model_name='forum',
            name='sync',
            field=models.CharField(help_text=b'When sync source is set, new topics and messages can not be created. Instead, sync messages are collated into topics and replies by helper scripts', max_length=64, null=True, verbose_name='Sync From', blank=True),
        ),
        migrations.AddField(
            model_name='forumtopic',
            name='message_id',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='forum',
            name='content_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', help_text=b'When fixed content is set, new topics can not be created. Instead, commented items are automatically posted as topics.', null=True, verbose_name='Fixed Content From'),
        ),
    ]
