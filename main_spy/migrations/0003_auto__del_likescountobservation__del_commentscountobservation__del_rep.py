# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'LikesCountObservation'
        db.delete_table('main_spy_likescountobservation')

        # Deleting model 'CommentsCountObservation'
        db.delete_table('main_spy_commentscountobservation')

        # Deleting model 'RepostsCountObservation'
        db.delete_table('main_spy_repostscountobservation')

        # Adding model 'Observation'
        db.create_table('main_spy_observation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=0)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'], null=True)),
            ('statistics', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
        ))
        db.send_create_signal('main_spy', ['Observation'])


    def backwards(self, orm):
        
        # Adding model 'LikesCountObservation'
        db.create_table('main_spy_likescountobservation', (
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=0)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main_spy', ['LikesCountObservation'])

        # Adding model 'CommentsCountObservation'
        db.create_table('main_spy_commentscountobservation', (
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=0)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main_spy', ['CommentsCountObservation'])

        # Adding model 'RepostsCountObservation'
        db.create_table('main_spy_repostscountobservation', (
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=0)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main_spy', ['RepostsCountObservation'])

        # Deleting model 'Observation'
        db.delete_table('main_spy_observation')


    models = {
        'main_spy.group': {
            'Meta': {'object_name': 'Group'},
            'gid': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main_spy.observation': {
            'Meta': {'object_name': 'Observation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']", 'null': 'True'}),
            'statistics': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'main_spy.post': {
            'Meta': {'object_name': 'Post'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'first_comment_date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scanned': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'pid': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'main_spy.postattachment': {
            'Meta': {'object_name': 'PostAttachment'},
            'attachment_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']", 'null': 'True'})
        }
    }

    complete_apps = ['main_spy']
