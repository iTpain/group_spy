# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Group.last_scanned'
        db.add_column('main_spy_group', 'last_scanned', self.gf('django.db.models.fields.DateTimeField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Group.last_scanned'
        db.delete_column('main_spy_group', 'last_scanned')


    models = {
        'main_spy.group': {
            'Meta': {'object_name': 'Group'},
            'gid': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scanned': ('django.db.models.fields.DateTimeField', [], {'default': '0'})
        },
        'main_spy.groupobservation': {
            'Meta': {'object_name': 'GroupObservation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        },
        'main_spy.postobservation': {
            'Meta': {'object_name': 'PostObservation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']", 'null': 'True'}),
            'statistics': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['main_spy']
