# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Post.author_is_group'
        db.add_column('main_spy_post', 'author_is_group', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Post.author_is_group'
        db.delete_column('main_spy_post', 'author_is_group')


    models = {
        'main_spy.demogeogroupobservation': {
            'Meta': {'object_name': 'DemogeoGroupObservation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'whole_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'main_spy.group': {
            'Meta': {'object_name': 'Group'},
            'agency': ('django.db.models.fields.TextField', [], {}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'brand': ('django.db.models.fields.TextField', [], {}),
            'gid': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_scanned': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'social_network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.SocialNetwork']", 'null': 'True', 'blank': 'True'}),
            'text_categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main_spy.TextCategory']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'main_spy.groupobservation': {
            'Meta': {'object_name': 'GroupObservation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'statistics': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'main_spy.latestpostobservation': {
            'Meta': {'object_name': 'LatestPostObservation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']", 'null': 'True'}),
            'statistics': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'main_spy.post': {
            'Meta': {'object_name': 'Post'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.User']", 'null': 'True'}),
            'author_is_group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': '0'}),
            'first_comment_date': ('django.db.models.fields.DateTimeField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_comment_date': ('django.db.models.fields.DateTimeField', [], {}),
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
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']", 'null': 'True'}),
            'statistics': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'main_spy.posttextcategoryassignment': {
            'Meta': {'object_name': 'PostTextCategoryAssignment'},
            'assigned_by_human': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.TextCategory']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']"})
        },
        'main_spy.scanstats': {
            'Meta': {'object_name': 'ScanStats'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scanner_class': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'time_taken': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'main_spy.socialnetwork': {
            'Meta': {'object_name': 'SocialNetwork'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'snid': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'main_spy.textcategory': {
            'Meta': {'object_name': 'TextCategory'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main_spy.user': {
            'Meta': {'object_name': 'User'},
            'age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'city_alias': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'education': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_man': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'last_scanned': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'snid': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'social_network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.SocialNetwork']", 'null': 'True'})
        },
        'main_spy.usersocialaction': {
            'Meta': {'object_name': 'UserSocialAction'},
            'comments': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'likes': ('django.db.models.fields.IntegerField', [], {}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.User']"})
        }
    }

    complete_apps = ['main_spy']
