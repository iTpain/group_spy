# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Group'
        db.create_table('main_spy_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gid', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('main_spy', ['Group'])

        # Adding model 'Post'
        db.create_table('main_spy_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pid', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=0)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('last_scanned', self.gf('django.db.models.fields.DateTimeField')(default=0)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('first_comment_date', self.gf('django.db.models.fields.DateTimeField')(default=0)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Group'])),
        ))
        db.send_create_signal('main_spy', ['Post'])

        # Adding model 'PostAttachment'
        db.create_table('main_spy_postattachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'])),
            ('attachment_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('main_spy', ['PostAttachment'])

        # Adding model 'CommentsCountObservation'
        db.create_table('main_spy_commentscountobservation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=0)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main_spy', ['CommentsCountObservation'])

        # Adding model 'LikesCountObservation'
        db.create_table('main_spy_likescountobservation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=0)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main_spy', ['LikesCountObservation'])

        # Adding model 'RepostsCountObservation'
        db.create_table('main_spy_repostscountobservation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=0)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main_spy', ['RepostsCountObservation'])


    def backwards(self, orm):
        
        # Deleting model 'Group'
        db.delete_table('main_spy_group')

        # Deleting model 'Post'
        db.delete_table('main_spy_post')

        # Deleting model 'PostAttachment'
        db.delete_table('main_spy_postattachment')

        # Deleting model 'CommentsCountObservation'
        db.delete_table('main_spy_commentscountobservation')

        # Deleting model 'LikesCountObservation'
        db.delete_table('main_spy_likescountobservation')

        # Deleting model 'RepostsCountObservation'
        db.delete_table('main_spy_repostscountobservation')


    models = {
        'main_spy.commentscountobservation': {
            'Meta': {'object_name': 'CommentsCountObservation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'main_spy.group': {
            'Meta': {'object_name': 'Group'},
            'gid': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main_spy.likescountobservation': {
            'Meta': {'object_name': 'LikesCountObservation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']"})
        },
        'main_spy.repostscountobservation': {
            'Meta': {'object_name': 'RepostsCountObservation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['main_spy']
