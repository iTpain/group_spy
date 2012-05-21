from django.db import models

class ScanStats(models.Model):
    date = models.DateTimeField(auto_now=True, auto_now_add=True)
    time_taken = models.BigIntegerField()
    scanner_class = models.CharField(max_length=32)

class TextCategory(models.Model):
    alias = models.CharField(max_length=256)

class SocialNetwork(models.Model):
    snid = models.CharField(max_length=256)
    alias = models.CharField(max_length=256)

class User(models.Model):
    snid = models.BigIntegerField(db_index=True)
    first_name = models.CharField(max_length=64, null=True)
    last_name = models.CharField(max_length=64, null=True)
    age = models.IntegerField(db_index=True, null=True)
    education = models.IntegerField(null=True)
    is_man = models.BooleanField()
    city_alias = models.CharField(max_length=64, null=True)
    last_scanned = models.DateTimeField(db_index=True, null=True)
    social_network = models.ForeignKey(SocialNetwork, null=True)
    
    def __str__(self):
        return "<" + str(self.id) + " snid=" + str(self.snid) + ">"

class Group(models.Model):
    gid = models.CharField(max_length=256)
    last_scanned = models.DateTimeField(auto_now=True, auto_now_add=True)
    agency = models.TextField()
    brand = models.TextField()
    alias = models.CharField(max_length=1024)
    social_network = models.ForeignKey(SocialNetwork, null=True, blank=True)
    text_categories = models.ManyToManyField(TextCategory, blank=True)

class Post(models.Model):
    pid = models.CharField(max_length=256)
    author = models.ForeignKey(User, null=True)
    author_is_group = models.BooleanField()
    date = models.DateTimeField(default=0)
    text = models.TextField()
    last_scanned = models.DateTimeField(auto_now=True, auto_now_add=True)
    closed = models.BooleanField(default=False)
    first_comment_date = models.DateTimeField()
    last_comment_date = models.DateTimeField()
    group = models.ForeignKey(Group)
    
    def __str__(self):
        return "<" + str(self.pid) + " closed=" + str(self.closed) + ">"
    
class PostAttachment(models.Model):
    post = models.ForeignKey(Post, null=True)
    attachment_type = models.CharField(max_length=32)
    
    def __str__(self):
        return "<" + str(self.post) + ", " + str(self.attachment_type) + ">"

class PostObservation(models.Model):
    date = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)
    value = models.IntegerField()
    post = models.ForeignKey(Post, null=True, db_index=True)
    statistics = models.CharField(max_length=32, db_index=True)
    
    def __str__(self):
        return "<" + str(self.post_id) + ", " + str(self.statistics) + ", " + str(self.value) + ">"
    
class LatestPostObservation(models.Model):
    value = models.IntegerField()
    post = models.ForeignKey(Post, null=True, db_index=True)
    statistics = models.CharField(max_length=32, db_index=True)
    
    def __str__(self):
        return "<" + str(self.post_id) + ", " + str(self.value) + ">"
    
class GroupObservation(models.Model):
    date = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)
    value = models.IntegerField()
    group = models.ForeignKey(Group)
    statistics = models.CharField(max_length=32, db_index=True)
    
class DemogeoGroupObservation(models.Model):
    date = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)
    group = models.ForeignKey(Group)
    json = models.TextField()
    whole_group = models.BooleanField()
    
class LatestDemogeoObservation(models.Model):
    json = models.TextField()
    group = models.ForeignKey(Group)
    #proper values are 'vk_viewers', 'entire', 'active'
    source = models.CharField(max_length=16)
    
class DemoObservation(models.Model):
    date = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)
    value = models.IntegerField()
    group = models.ForeignKey(Group)
    # the high value of age strata, e.g. for '15-18' the age group's value is 18
    source = models.CharField(max_length=16)
    age_group = models.IntegerField()
    is_man = models.BooleanField()
    
class UserSocialAction(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)
    type = models.CharField(max_length=32)
    content_id = models.CharField(max_length=128)
    date = models.DateTimeField()
    
class PostTextCategoryAssignment (models.Model):
    date = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True)
    post = models.ForeignKey(Post)
    category = models.ForeignKey(TextCategory)
    assigned_by_human = models.BooleanField()
    
    