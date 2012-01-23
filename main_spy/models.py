from django.db import models

class Group(models.Model):
    gid = models.CharField(max_length=256)
    last_scanned = models.DateTimeField(auto_now=True, auto_now_add=True)
    agency = models.TextField()
    brand = models.TextField()
    alias = models.CharField(max_length=1024)

class Post(models.Model):
    pid = models.CharField(max_length=256)
    date = models.DateTimeField(default=0)
    text = models.TextField()
    last_scanned = models.DateTimeField(auto_now=True, auto_now_add=True)
    closed = models.BooleanField(default=False)
    first_comment_date = models.DateTimeField(auto_now=True, auto_now_add=True)
    last_comment_date = models.DateTimeField(auto_now=True, auto_now_add=True)
    group = models.ForeignKey(Group)
    
class PostAttachment(models.Model):
    post = models.ForeignKey(Post, null=True)
    attachment_type = models.CharField(max_length=32)

class PostObservation(models.Model):
    date = models.DateTimeField(auto_now=True, auto_now_add=True)
    value = models.IntegerField()
    post = models.ForeignKey(Post, null=True)
    statistics = models.CharField(max_length=32, db_index=True)
    
class GroupObservation(models.Model):
    date = models.DateTimeField(auto_now=True, auto_now_add=True)
    value = models.IntegerField()
    group = models.ForeignKey(Group)
    statistics = models.CharField(max_length=32, db_index=True)