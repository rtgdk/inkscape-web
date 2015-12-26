# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.storage.django_orm

class CreateModel(migrations.CreateModel):
    def state_forwards(self, app_label, state):
        return super(CreateModel, self).state_forwards('default', state)

class AlterUniqueTogether(migrations.AlterUniqueTogether):
    def state_forwards(self, app_label, state):
        return super(AlterUniqueTogether, self).state_forwards('default', state)

class Migration(migrations.Migration):

    dependencies = [
        ('inkscape', '0001_initial'),
        ('default', '0001_initial'),
    ]

    run_before = [
        ('default', '0002_add_related_name'),
    ]

    operations = [
        CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True,
                    primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('code', models.CharField(max_length=32, db_index=True)),
                ('verified', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'social_auth_code',
            },
            bases=(models.Model, social.storage.django_orm.DjangoCodeMixin),
        ),
        AlterUniqueTogether(
            name='usersocialauth',
            unique_together=set([('provider', 'uid')]),
        ),
        AlterUniqueTogether(
            name='code',
            unique_together=set([('email', 'code')]),
        ),
        AlterUniqueTogether(
            name='nonce',
            unique_together=set([('server_url', 'timestamp', 'salt')]),
        ),
    ]
