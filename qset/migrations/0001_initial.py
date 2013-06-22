# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Subject'
        db.create_table(u'qset_subject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'qset', ['Subject'])

        # Adding model 'Question'
        db.create_table(u'qset_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qset.Subject'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['usermanage.Group'], null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_used', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('choice_w', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('choice_x', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('choice_y', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('choice_z', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal(u'qset', ['Question'])

        # Adding model 'Set'
        db.create_table(u'qset_set', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['usermanage.Group'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('is_used', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal(u'qset', ['Set'])

        # Adding M2M table for field subjects on 'Set'
        m2m_table_name = db.shorten_name(u'qset_set_subjects')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('set', models.ForeignKey(orm[u'qset.set'], null=False)),
            ('subject', models.ForeignKey(orm[u'qset.subject'], null=False))
        ))
        db.create_unique(m2m_table_name, ['set_id', 'subject_id'])

        # Adding model 'Set_questions'
        db.create_table(u'qset_set_questions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qset.Set'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qset.Question'])),
            ('q_num', self.gf('django.db.models.fields.IntegerField')()),
            ('q_type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'qset', ['Set_questions'])

        # Adding model 'Round'
        db.create_table(u'qset_round', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qset.Set'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['usermanage.Group'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'qset', ['Round'])

        # Adding M2M table for field players on 'Round'
        m2m_table_name = db.shorten_name(u'qset_round_players')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('round', models.ForeignKey(orm[u'qset.round'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['round_id', 'user_id'])

        # Adding model 'Score'
        db.create_table(u'qset_score', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qset.Round'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qset.Set_questions'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('score', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('score_val', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'qset', ['Score'])


    def backwards(self, orm):
        # Deleting model 'Subject'
        db.delete_table(u'qset_subject')

        # Deleting model 'Question'
        db.delete_table(u'qset_question')

        # Deleting model 'Set'
        db.delete_table(u'qset_set')

        # Removing M2M table for field subjects on 'Set'
        db.delete_table(db.shorten_name(u'qset_set_subjects'))

        # Deleting model 'Set_questions'
        db.delete_table(u'qset_set_questions')

        # Deleting model 'Round'
        db.delete_table(u'qset_round')

        # Removing M2M table for field players on 'Round'
        db.delete_table(db.shorten_name(u'qset_round_players'))

        # Deleting model 'Score'
        db.delete_table(u'qset_score')


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
        u'qset.question': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'Question'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'choice_w': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'choice_x': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'choice_y': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'choice_z': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['usermanage.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_used': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qset.Subject']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'qset.round': {
            'Meta': {'object_name': 'Round'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['usermanage.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qset.Set']"})
        },
        u'qset.score': {
            'Meta': {'object_name': 'Score'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qset.Set_questions']"}),
            'round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qset.Round']"}),
            'score': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'score_val': ('django.db.models.fields.IntegerField', [], {})
        },
        u'qset.set': {
            'Meta': {'object_name': 'Set'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['usermanage.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_used': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['qset.Question']", 'through': u"orm['qset.Set_questions']", 'symmetrical': 'False'}),
            'subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['qset.Subject']", 'symmetrical': 'False'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'qset.set_questions': {
            'Meta': {'object_name': 'Set_questions'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q_num': ('django.db.models.fields.IntegerField', [], {}),
            'q_type': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qset.Question']"}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qset.Set']"})
        },
        u'qset.subject': {
            'Meta': {'object_name': 'Subject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'usermanage.group': {
            'Meta': {'object_name': 'Group'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'through': u"orm['usermanage.Membership']", 'symmetrical': 'False'})
        },
        u'usermanage.membership': {
            'Meta': {'object_name': 'Membership'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['usermanage.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['qset']