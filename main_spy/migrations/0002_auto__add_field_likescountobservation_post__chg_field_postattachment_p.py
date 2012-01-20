# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'LikesCountObservation.post'
        db.add_column('main_spy_likescountobservation', 'post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'], null=True), keep_default=False)

        # Changing field 'PostAttachment.post'
        db.alter_column('main_spy_postattachment', 'post_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'], null=True))

        # Adding field 'CommentsCountObservation.post'
        db.add_column('main_spy_commentscountobservation', 'post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'], null=True), keep_default=False)

        # Adding field 'RepostsCountObservation.post'
        db.add_column('main_spy_repostscountobservation', 'post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'], null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'LikesCountObservation.post'
        db.delete_column('main_spy_likescountobservation', 'post_id')

        # Changing field 'PostAttachment.post'
        db.alter_column('main_spy_postattachment', 'post_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['main_spy.Post']))

        # Deleting field 'CommentsCountObservation.post'
        db.delete_column('main_spy_commentscountobservation', 'post_id')

        # Deleting field 'RepostsCountObservation.post'
        db.delete_column('main_spy_repostscountobservation', 'post_id')


    models = {
        'main_spy.commentscountobservation': {
            'Meta': {'object_name': 'CommentsCountObservation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']", 'null': 'True'}),
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
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']", 'null': 'True'}),
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
        },
        'main_spy.repostscountobservation': {
            'Meta': {'object_name': 'RepostsCountObservation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']", 'null': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['main_spy']
