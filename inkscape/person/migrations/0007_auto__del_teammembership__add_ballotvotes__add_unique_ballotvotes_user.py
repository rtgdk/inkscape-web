# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TeamMembership'
        db.delete_table(u'person_teammembership')

        # Adding model 'BallotVotes'
        db.create_table(u'person_ballotvotes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ballot', self.gf('django.db.models.fields.related.ForeignKey')(related_name='votes', to=orm['person.Ballot'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ballot_votes', to=orm['auth.User'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='votes', to=orm['person.BallotItem'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'person', ['BallotVotes'])

        # Adding unique constraint on 'BallotVotes', fields ['user', 'item', 'order']
        db.create_unique(u'person_ballotvotes', ['user_id', 'item_id', 'order'])

        # Adding model 'Ballot'
        db.create_table(u'person_ballot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ballots', to=orm['person.Team'])),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'person', ['Ballot'])

        # Adding model 'BallotItem'
        db.create_table(u'person_ballotitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ballot', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['person.Ballot'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'person', ['BallotItem'])

        # Deleting field 'Team.worker'
        db.delete_column(u'person_team', 'worker_id')

        # Adding field 'Team.members'
        db.add_column(u'person_team', 'members',
                      self.gf('pile.fields.AutoOneToOneField')(blank=True, related_name='team', unique=True, null=True, to=orm['auth.Group']),
                      keep_default=False)

        # Adding field 'Team.slug'
        db.add_column(u'person_team', 'slug',
                      self.gf('django.db.models.fields.SlugField')(default='slug', max_length=32),
                      keep_default=False)

        # Adding M2M table for field watchers on 'Team'
        m2m_table_name = db.shorten_name(u'person_team_watchers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm[u'person.team'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['team_id', 'user_id'])


        # Changing field 'Team.admin'
        db.alter_column(u'person_team', 'admin_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

    def backwards(self, orm):
        # Removing unique constraint on 'BallotVotes', fields ['user', 'item', 'order']
        db.delete_unique(u'person_ballotvotes', ['user_id', 'item_id', 'order'])

        # Adding model 'TeamMembership'
        db.create_table(u'person_teammembership', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='teams', to=orm['auth.User'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['person.Team'])),
        ))
        db.send_create_signal(u'person', ['TeamMembership'])

        # Deleting model 'BallotVotes'
        db.delete_table(u'person_ballotvotes')

        # Deleting model 'Ballot'
        db.delete_table(u'person_ballot')

        # Deleting model 'BallotItem'
        db.delete_table(u'person_ballotitem')

        # Adding field 'Team.worker'
        db.add_column(u'person_team', 'worker',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='teams', null=True, to=orm['auth.Group'], blank=True),
                      keep_default=False)

        # Deleting field 'Team.members'
        db.delete_column(u'person_team', 'members_id')

        # Deleting field 'Team.slug'
        db.delete_column(u'person_team', 'slug')

        # Removing M2M table for field watchers on 'Team'
        db.delete_table(db.shorten_name(u'person_team_watchers'))


        # Changing field 'Team.admin'
        db.alter_column(u'person_team', 'admin_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.Group']))

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
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'person.ballot': {
            'Meta': {'object_name': 'Ballot'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ballots'", 'to': u"orm['person.Team']"})
        },
        u'person.ballotitem': {
            'Meta': {'object_name': 'BallotItem'},
            'ballot': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['person.Ballot']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'person.ballotvotes': {
            'Meta': {'unique_together': "(('user', 'item', 'order'),)", 'object_name': 'BallotVotes'},
            'ballot': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': u"orm['person.Ballot']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': u"orm['person.BallotItem']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ballot_votes'", 'to': u"orm['auth.User']"})
        },
        u'person.groupphotoplugin': {
            'Meta': {'object_name': 'GroupPhotoPlugin', '_ormbases': ['cms.CMSPlugin']},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            'style': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'person.team': {
            'Meta': {'object_name': 'Team'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'teams'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enrole': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'mailman': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'members': ('pile.fields.AutoOneToOneField', [], {'blank': 'True', 'related_name': "'team'", 'unique': 'True', 'null': 'True', 'to': u"orm['auth.Group']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '32'}),
            'watchers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'watches'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['auth.User']"})
        },
        u'person.userdetails': {
            'Meta': {'object_name': 'UserDetails'},
            'bio': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dauser': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'gpg_key': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ircdev': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ircnick': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'ircpass': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ocuser': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'photo': ('pile.fields.ResizedImageField', [], {'name': "'photo'", 'max_height': '190', 'max_length': '100', 'max_width': '190', 'blank': 'True', 'null': 'True'}),
            'tbruser': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'user': ('pile.fields.AutoOneToOneField', [], {'related_name': "'details'", 'unique': 'True', 'to': u"orm['auth.User']"}),
            'visits': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['person']