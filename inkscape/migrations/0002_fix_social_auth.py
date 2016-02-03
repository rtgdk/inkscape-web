# -*- coding: utf-8 -*-
#
# This migration is for app 'default' not inkscape.
#
from __future__ import unicode_literals

from django.db import migrations, models
import social.storage.django_orm

class AnotherAppMixin(object):
    @property
    def replacement_app(self):
        raise NotImplementedError("You should specify the replacement_app name.")

    def state_forwards(self, app_label, *args):
        return super(AnotherAppMixin, self).state_forwards(self.replacement_app, *args)

    def database_forwards(self, app_label, *args): 
        return super(AnotherAppMixin, self).database_forwards(self.replacement_app, *args)

    def database_backwards(self, app_label, *args):
        return super(AnotherAppMixin, self).database_backwards(self.replacement_app, *args)


class CreateModel(AnotherAppMixin, migrations.CreateModel):
    replacement_app = 'default'

class AlterUniqueTogether(AnotherAppMixin, migrations.AlterUniqueTogether):
    replacement_app = 'default'

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
