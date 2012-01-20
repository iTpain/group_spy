# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'GroupObservation.date'
        db.alter_column('main_spy_groupobservation', 'date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))

        # Adding field 'Group.alias'
        db.add_column('main_spy_group', 'alias', self.gf('django.db.models.fields.CharField')(default='', max_length=1024), keep_default=False)

        # Adding field 'Group.link'
        db.add_column('main_spy_group', 'link', self.gf('django.db.models.fields.CharField')(default='', max_length=1024), keep_default=False)

        # Changing field 'Group.last_scanned'
        db.alter_column('main_spy_group', 'last_scanned', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))

        # Changing field 'PostObservation.date'
        db.alter_column('main_spy_postobservation', 'date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))

        # Changing field 'Post.last_scanned'
        db.alter_column('main_spy_post', 'last_scanned', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))

        # Changing field 'Post.first_comment_date'
        db.alter_column('main_spy_post', 'first_comment_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True))


    def backwards(self, orm):
        
        # Changing field 'GroupObservation.date'
        db.alter_column('main_spy_groupobservation', 'date', self.gf('django.db.models.fields.DateTimeField')())

        # Deleting field 'Group.alias'
        db.delete_column('main_spy_group', 'alias')

        # Deleting field 'Group.link'
        db.delete_column('main_spy_group', 'link')

        # Changing field 'Group.last_scanned'
        db.alter_column('main_spy_group', 'last_scanned', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'PostObservation.date'
        db.alter_column('main_spy_postobservation', 'date', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Post.last_scanned'
        db.alter_column('main_spy_post', 'last_scanned', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Post.first_comment_date'
        db.alter_column('main_spy_post', 'first_comment_date', self.gf('django.db.models.fields.DateTimeField')())


    models = {
        'main_spy.group': {
            'Meta': {'object_name': 'Group'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'gid': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scanned': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'main_spy.groupobservation': {
            'Meta': {'object_name': 'GroupObservation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'statistics': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'main_spy.post': {
            'Meta': {'object_name': 'Post'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'first_comment_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scanned': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
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
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']", 'null': 'True'}),
            'statistics': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['main_spy']
