# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DemogeoGroupObservation'
        db.create_table('main_spy_demogeogroupobservation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, db_index=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Group'])),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('whole_group', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('main_spy', ['DemogeoGroupObservation'])

        # Adding model 'VKUser'
        db.create_table('main_spy_vkuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vkid', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('age', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('education', self.gf('django.db.models.fields.IntegerField')()),
            ('is_man', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('city_alias', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('last_scanned', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
        ))
        db.send_create_signal('main_spy', ['VKUser'])

        # Adding model 'VKUserSocialAction'
        db.create_table('main_spy_vkusersocialaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.VKUser'])),
            ('likes', self.gf('django.db.models.fields.IntegerField')()),
            ('comments', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main_spy', ['VKUserSocialAction'])


    def backwards(self, orm):
        
        # Deleting model 'DemogeoGroupObservation'
        db.delete_table('main_spy_demogeogroupobservation')

        # Deleting model 'VKUser'
        db.delete_table('main_spy_vkuser')

        # Deleting model 'VKUserSocialAction'
        db.delete_table('main_spy_vkusersocialaction')


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
            'last_scanned': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
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
        'main_spy.vkuser': {
            'Meta': {'object_name': 'VKUser'},
            'age': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'city_alias': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'education': ('django.db.models.fields.IntegerField', [], {}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_man': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'last_scanned': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'vkid': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'})
        },
        'main_spy.vkusersocialaction': {
            'Meta': {'object_name': 'VKUserSocialAction'},
            'comments': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'likes': ('django.db.models.fields.IntegerField', [], {}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.VKUser']"})
        }
    }

    complete_apps = ['main_spy']
