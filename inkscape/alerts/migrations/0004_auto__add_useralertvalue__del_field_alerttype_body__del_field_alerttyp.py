# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserAlertValue'
        db.create_table(u'alerts_useralertvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alert', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['alerts.UserAlert'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('target', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'alerts', ['UserAlertValue'])

        # Deleting field 'AlertType.body'
        db.delete_column(u'alerts_alerttype', 'body')

        # Deleting field 'AlertType.desc'
        db.delete_column(u'alerts_alerttype', 'desc')

        # Deleting field 'AlertType.name'
        db.delete_column(u'alerts_alerttype', 'name')

        # Deleting field 'AlertType.email_body'
        db.delete_column(u'alerts_alerttype', 'email_body')

        # Deleting field 'AlertType.email_subject'
        db.delete_column(u'alerts_alerttype', 'email_subject')

        # Deleting field 'AlertType.subject'
        db.delete_column(u'alerts_alerttype', 'subject')


        # Changing field 'AlertType.created'
        db.alter_column(u'alerts_alerttype', 'created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=datetime.datetime.now))
        # Deleting field 'AlertSubscription.table'
        db.delete_column(u'alerts_alertsubscription', 'table_id')

        # Deleting field 'AlertSubscription.o_id'
        db.delete_column(u'alerts_alertsubscription', 'o_id')

        # Adding field 'AlertSubscription.target'
        db.add_column(u'alerts_alertsubscription', 'target',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'UserAlertValue'
        db.delete_table(u'alerts_useralertvalue')

        # Adding field 'AlertType.body'
        db.add_column(u'alerts_alerttype', 'body',
                      self.gf('django.db.models.fields.TextField')(default='None'),
                      keep_default=False)

        # Adding field 'AlertType.desc'
        db.add_column(u'alerts_alerttype', 'desc',
                      self.gf('django.db.models.fields.CharField')(default='None', max_length=255),
                      keep_default=False)

        # Adding field 'AlertType.name'
        db.add_column(u'alerts_alerttype', 'name',
                      self.gf('django.db.models.fields.CharField')(default='None', max_length=64),
                      keep_default=False)

        # Adding field 'AlertType.email_body'
        db.add_column(u'alerts_alerttype', 'email_body',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'AlertType.email_subject'
        db.add_column(u'alerts_alerttype', 'email_subject',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'AlertType.subject'
        db.add_column(u'alerts_alerttype', 'subject',
                      self.gf('django.db.models.fields.CharField')(default='None', max_length=255),
                      keep_default=False)


        # Changing field 'AlertType.created'
        db.alter_column(u'alerts_alerttype', 'created', self.gf('django.db.models.fields.DateTimeField')())
        # Adding field 'AlertSubscription.table'
        db.add_column(u'alerts_alertsubscription', 'table',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'AlertSubscription.o_id'
        db.add_column(u'alerts_alertsubscription', 'o_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True),
                      keep_default=False)

        # Deleting field 'AlertSubscription.target'
        db.delete_column(u'alerts_alertsubscription', 'target')


    models = {
        u'alerts.alertsubscription': {
            'Meta': {'object_name': 'AlertSubscription'},
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscriptions'", 'to': u"orm['alerts.AlertType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alert_subscriptions'", 'to': u"orm['auth.User']"})
        },
        u'alerts.alerttype': {
            'Meta': {'object_name': 'AlertType'},
            'category': ('django.db.models.fields.CharField', [], {'default': "'?'", 'max_length': '1'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'datetime.datetime.now', 'blank': 'True'}),
            'default_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default_hide': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'alerts.message': {
            'Meta': {'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': u"orm['auth.User']"}),
            'reply_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'replies'", 'null': 'True', 'to': u"orm['alerts.Message']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': u"orm['auth.User']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'alerts.useralert': {
            'Meta': {'object_name': 'UserAlert'},
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent'", 'to': u"orm['alerts.AlertType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alerts'", 'to': u"orm['auth.User']"}),
            'viewed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'alerts.useralertobject': {
            'Meta': {'object_name': 'UserAlertObject'},
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'objects'", 'to': u"orm['alerts.UserAlert']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'o_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'})
        },
        u'alerts.useralertsetting': {
            'Meta': {'object_name': 'UserAlertSetting'},
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'settings'", 'to': u"orm['alerts.AlertType']"}),
            'email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hide': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alert_settings'", 'to': u"orm['auth.User']"})
        },
        u'alerts.useralertvalue': {
            'Meta': {'object_name': 'UserAlertValue'},
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['alerts.UserAlert']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['alerts']