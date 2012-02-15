# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'VKUser'
        db.delete_table('main_spy_vkuser')

        # Deleting model 'VKUserSocialAction'
        db.delete_table('main_spy_vkusersocialaction')

        # Adding model 'User'
        db.create_table('main_spy_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snid', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('age', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('education', self.gf('django.db.models.fields.IntegerField')()),
            ('is_man', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('city_alias', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('last_scanned', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('social_network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.SocialNetwork'], null=True)),
        ))
        db.send_create_signal('main_spy', ['User'])

        # Adding model 'UserSocialAction'
        db.create_table('main_spy_usersocialaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.User'])),
            ('likes', self.gf('django.db.models.fields.IntegerField')()),
            ('comments', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main_spy', ['UserSocialAction'])

        # Adding field 'Post.author'
        db.add_column('main_spy_post', 'author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.User'], null=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding model 'VKUser'
        db.create_table('main_spy_vkuser', (
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('last_scanned', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('vkid', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('is_man', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('age', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('education', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city_alias', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('main_spy', ['VKUser'])

        # Adding model 'VKUserSocialAction'
        db.create_table('main_spy_vkusersocialaction', (
            ('comments', self.gf('django.db.models.fields.IntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.VKUser'])),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_spy.Post'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('likes', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('main_spy', ['VKUserSocialAction'])

        # Deleting model 'User'
        db.delete_table('main_spy_user')

        # Deleting model 'UserSocialAction'
        db.delete_table('main_spy_usersocialaction')

        # Deleting field 'Post.author'
        db.delete_column('main_spy_post', 'author_id')


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
        'main_spy.user': {
            'Meta': {'object_name': 'User'},
            'age': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'city_alias': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'education': ('django.db.models.fields.IntegerField', [], {}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_man': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'last_scanned': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
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
