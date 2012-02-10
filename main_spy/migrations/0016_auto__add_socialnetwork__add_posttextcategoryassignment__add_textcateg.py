# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SocialNetwork'
        db.create_table('main_spy_socialnetwork', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snid', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('main_spy', ['SocialNetwork'])

        # Adding model 'PostTextCategoryAssignment'
        db.create_table('main_spy_posttextcategoryassignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, db_index=True, blank=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.TextCategory'])),
            ('assigned_by_human', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('main_spy', ['PostTextCategoryAssignment'])

        # Adding model 'TextCategory'
        db.create_table('main_spy_textcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('main_spy', ['TextCategory'])

        # Adding field 'Group.social_network'
        db.add_column('main_spy_group', 'social_network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.SocialNetwork'], null=True), keep_default=False)

        # Adding M2M table for field text_categories on 'Group'
        db.create_table('main_spy_group_text_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['main_spy.group'], null=False)),
            ('textcategory', models.ForeignKey(orm['main_spy.textcategory'], null=False))
        ))
        db.create_unique('main_spy_group_text_categories', ['group_id', 'textcategory_id'])


    def backwards(self, orm):
        
        # Deleting model 'SocialNetwork'
        db.delete_table('main_spy_socialnetwork')

        # Deleting model 'PostTextCategoryAssignment'
        db.delete_table('main_spy_posttextcategoryassignment')

        # Deleting model 'TextCategory'
        db.delete_table('main_spy_textcategory')

        # Deleting field 'Group.social_network'
        db.delete_column('main_spy_group', 'social_network_id')

        # Removing M2M table for field text_categories on 'Group'
        db.delete_table('main_spy_group_text_categories')


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
            'social_network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.SocialNetwork']", 'null': 'True'}),
            'text_categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main_spy.TextCategory']", 'symmetrical': 'False'})
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
        'main_spy.posttextcategoryassignment': {
            'Meta': {'object_name': 'PostTextCategoryAssignment'},
            'assigned_by_human': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.TextCategory']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_spy.Post']"})
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
