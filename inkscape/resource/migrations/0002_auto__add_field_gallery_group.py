# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Gallery.group'
        db.add_column(u'resource_gallery', 'group',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='galleries', null=True, to=orm['auth.Group']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Gallery.group'
        db.delete_column(u'resource_gallery', 'group_id')


    models = {
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'resource.category': {
            'Meta': {'object_name': 'Category'},
            'acceptable_licenses': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['resource.License']", 'symmetrical': 'False'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'resource.gallery': {
            'Meta': {'object_name': 'Gallery'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'galleries'", 'null': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['resource.Resource']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'galleries'", 'to': u"orm['auth.User']"})
        },
        u'resource.license': {
            'Meta': {'object_name': 'License'},
            'at': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'banner': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'nc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nd': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'replaced': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['resource.License']", 'null': 'True', 'blank': 'True'}),
            'sa': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'resource.quota': {
            'Meta': {'object_name': 'Quota'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'quotas'", 'unique': 'True', 'null': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': '102400'})
        },
        u'resource.resource': {
            'Meta': {'object_name': 'Resource'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'items'", 'null': 'True', 'to': u"orm['resource.Category']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'downed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'media_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thumbnail': ('inkscape.fields.ResizedImageField', [], {'name': "'thumbnail'", 'max_height': '190', 'max_length': '100', 'max_width': '190', 'blank': 'True', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources'", 'to': u"orm['auth.User']"}),
            'viewed': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'resource.resourcefile': {
            'Meta': {'object_name': 'ResourceFile', '_ormbases': [u'resource.Resource']},
            'download': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['resource.License']", 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'resource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['resource.Resource']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'resource.vote': {
            'Meta': {'object_name': 'Vote'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': u"orm['resource.Resource']"}),
            'vote': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['resource']