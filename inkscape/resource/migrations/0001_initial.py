# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'License'
        db.create_table(u'resource_license', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('banner', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('icon', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('at', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sa', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('nc', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('nd', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('replaced', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resource.License'], null=True, blank=True)),
        ))
        db.send_create_signal(u'resource', ['License'])

        # Adding model 'Category'
        db.create_table(u'resource_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'resource', ['Category'])

        # Adding M2M table for field acceptable_licenses on 'Category'
        m2m_table_name = db.shorten_name(u'resource_category_acceptable_licenses')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm[u'resource.category'], null=False)),
            ('license', models.ForeignKey(orm[u'resource.license'], null=False))
        ))
        db.create_unique(m2m_table_name, ['category_id', 'license_id'])

        # Adding model 'Resource'
        db.create_table(u'resource_resource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resources', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='items', null=True, to=orm['resource.Category'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('edited', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('thumbnail', self.gf('inkscape.fields.ResizedImageField')(name='thumbnail', max_height=190, max_length=100, max_width=190, blank=True, null=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('viewed', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('downed', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('media_type', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
        ))
        db.send_create_signal(u'resource', ['Resource'])

        # Adding model 'ResourceFile'
        db.create_table(u'resource_resourcefile', (
            (u'resource_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['resource.Resource'], unique=True, primary_key=True)),
            ('download', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('license', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resource.License'], null=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'resource', ['ResourceFile'])

        # Adding model 'Gallery'
        db.create_table(u'resource_gallery', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='galleries', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'resource', ['Gallery'])

        # Adding M2M table for field items on 'Gallery'
        m2m_table_name = db.shorten_name(u'resource_gallery_items')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gallery', models.ForeignKey(orm[u'resource.gallery'], null=False)),
            ('resource', models.ForeignKey(orm[u'resource.resource'], null=False))
        ))
        db.create_unique(m2m_table_name, ['gallery_id', 'resource_id'])

        # Adding model 'Vote'
        db.create_table(u'resource_vote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(related_name='votes', to=orm['resource.Resource'])),
            ('voter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='votes', to=orm['auth.User'])),
            ('vote', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'resource', ['Vote'])

        # Adding model 'Quota'
        db.create_table(u'resource_quota', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='quotas', unique=True, null=True, to=orm['auth.Group'])),
            ('size', self.gf('django.db.models.fields.IntegerField')(default=102400)),
        ))
        db.send_create_signal(u'resource', ['Quota'])


    def backwards(self, orm):
        # Deleting model 'License'
        db.delete_table(u'resource_license')

        # Deleting model 'Category'
        db.delete_table(u'resource_category')

        # Removing M2M table for field acceptable_licenses on 'Category'
        db.delete_table(db.shorten_name(u'resource_category_acceptable_licenses'))

        # Deleting model 'Resource'
        db.delete_table(u'resource_resource')

        # Deleting model 'ResourceFile'
        db.delete_table(u'resource_resourcefile')

        # Deleting model 'Gallery'
        db.delete_table(u'resource_gallery')

        # Removing M2M table for field items on 'Gallery'
        db.delete_table(db.shorten_name(u'resource_gallery_items'))

        # Deleting model 'Vote'
        db.delete_table(u'resource_vote')

        # Deleting model 'Quota'
        db.delete_table(u'resource_quota')


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