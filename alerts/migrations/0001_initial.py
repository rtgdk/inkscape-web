# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.core.validators

from django.db.migrations.operations.base import Operation
class DeleteIfExists(Operation):
    """Delete a table if exists (ignores model)"""
    def __init__(self, table_name):
        self.table_name = table_name

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state): 
        if schema_editor.connection.vendor == 'mysql':
            schema_editor.execute("SET FOREIGN_KEY_CHECKS=0")
            try:
                schema_editor.execute("DROP TABLE IF EXISTS %(table)s CASCADE" % {
                    "table": schema_editor.quote_name(self.table_name),
                })
            except Exception as error:
                if 'Warning' not in type(error).__name__:
                    raise
            schema_editor.execute("SET FOREIGN_KEY_CHECKS=1")
        else:
            schema_editor.execute("DROP TABLE IF EXISTS %(table)s" % {
                "table": schema_editor.quote_name(self.table_name),
            })

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def describe(self):
        return "Delete %s table if exists" % self.table_name



class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        #DeleteIfExists('alerts_alertsubscription'),
        migrations.CreateModel(
            name='AlertSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target', models.PositiveIntegerField(null=True, verbose_name='Object ID', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        #DeleteIfExists('alerts_alerttype'),
        migrations.CreateModel(
            name='AlertType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(max_length=32, verbose_name='URL Slug')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('category', models.CharField(default=b'?', max_length=1, verbose_name='Type Category', choices=[(b'?', b'Unknown'), (b'U', b'User to User'), (b'S', b'System to User'), (b'A', b'Admin to User'), (b'P', b'User to Admin'), (b'T', b'System to Translator')])),
                ('enabled', models.BooleanField(default=False)),
                ('default_hide', models.BooleanField(default=False)),
                ('default_email', models.BooleanField(default=False)),
                ('group', models.ForeignKey(verbose_name='Limit to Group', blank=True, to='auth.Group', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        #DeleteIfExists('alerts_message'),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=128)),
                ('body', models.TextField(blank=True, null=True, verbose_name='Message Body', validators=[django.core.validators.MaxLengthValidator(8192)])),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('recipient', models.ForeignKey(related_name='messages', to=settings.AUTH_USER_MODEL)),
                ('reply_to', models.ForeignKey(related_name='replies', blank=True, to='alerts.Message', null=True)),
                ('sender', models.ForeignKey(related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        #DeleteIfExists('alerts_useralert'),
        migrations.CreateModel(
            name='UserAlert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('viewed', models.DateTimeField(null=True, blank=True)),
                ('deleted', models.DateTimeField(null=True, blank=True)),
                ('alert', models.ForeignKey(related_name='sent', to='alerts.AlertType')),
                ('user', models.ForeignKey(related_name='alerts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        #DeleteIfExists('alerts_useralertobject'),
        migrations.CreateModel(
            name='UserAlertObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('o_id', models.PositiveIntegerField(null=True)),
                ('alert', models.ForeignKey(related_name='objs', to='alerts.UserAlert')),
                ('table', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        #DeleteIfExists('alerts_useralertsetting'),
        migrations.CreateModel(
            name='UserAlertSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hide', models.BooleanField(default=True, verbose_name='Hide Alerts')),
                ('email', models.BooleanField(default=False, verbose_name='Send Email Alert')),
                ('alert', models.ForeignKey(related_name='settings', to='alerts.AlertType')),
                ('user', models.ForeignKey(related_name='alert_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserAlertValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('target', models.CharField(max_length=255)),
                ('alert', models.ForeignKey(related_name='values', to='alerts.UserAlert')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='alertsubscription',
            name='alert',
            field=models.ForeignKey(related_name='subscriptions', to='alerts.AlertType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alertsubscription',
            name='user',
            field=models.ForeignKey(related_name='alert_subscriptions', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
