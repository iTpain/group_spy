from group_spy.main_spy.models import Post, Group, PostObservation, PostAttachment, LatestPostObservation, User, UserSocialAction
from datetime import datetime, timedelta
from group_spy.crawler.vk import FailedRequestError
from group_spy.utils.misc import get_earliest_post_time
from django.db import DatabaseError
from group_spy import settings
import time

def iso_date_from_ts(ts):
    return datetime.fromtimestamp(ts).isoformat(' ')

class PostsScanner(object):
    
    @staticmethod
    def get_id():
        return 'post_scan'
    
    _stats = ['likes', 'reposts', 'comments']
    
    def scan(self, crawler):
        groups = Group.objects.all()
        for g in groups:
            try:
                self.find_new_posts(crawler, g.gid)
            except (FailedRequestError, DatabaseError) as e:
                print "PostScanner -- error while fetching or saving new posts for group " + str(g.gid) + " due to " + str(e)      
            self.update_group_posts(crawler, g.gid)
        print "Posts scan completed"
        
    def find_new_posts(self, crawler, gid):
        print "Fetching new posts for group " + str(gid)
        posts_to_add = []
        for p in crawler.get_posts_from_group("-" + str(gid)):
            try:
                Post.objects.get(pid=p['id'], group=gid)
                break
            except Post.DoesNotExist:
                posts_to_add.append(p)
        now = datetime.now()
        for p in posts_to_add:
            post_date = datetime.fromtimestamp(p['date'])
            author = None
            if p['from_id'] != -int(gid):
                author_is_group = False
                try:
                    author = User.objects.get(snid=p['from_id'])
                except User.DoesNotExist:
                    author = User(snid=p['from_id'])
                    author.save()
            else:
                author_is_group = True
            new_post = Post(pid=p['id'], author=author, author_is_group=author_is_group, date=post_date, text=p['text'], last_scanned=now, closed=False, first_comment_date=post_date, last_comment_date=post_date, group_id=gid)
            print "Post " + str(p['id']) + " added, date published: " + str(post_date) + " author: " + str(author) + " is group: " + str(author_is_group)
            new_post.save()
            for s in self._stats:
                latest_obs = LatestPostObservation(post=new_post, statistics=s, value=0)
                latest_obs.save()
            self.create_attachments_for_post (p, new_post)
                
    def create_attachments_for_post(self, vk_data, post):
        has_attachments = False
        if 'attachments' in vk_data:
            for attachment in vk_data['attachments']:
                db_attachment = PostAttachment(post=post, attachment_type=attachment['type'])
                db_attachment.save()
                has_attachments = True
                print "Attachment " + attachment["type"] + " added to post " + str(post.pid)
        if not has_attachments:
            db_attachment = PostAttachment(post=post, attachment_type='no_attachment')            
            db_attachment.save()   
            print "NO attachment added to post " + str(post.pid)         
    
    def update_group_posts(self, crawler, gid):
        active_posts = list(Post.objects.filter(closed=False, group=gid))
        # some rounding or conversion error has occured rarely from putting post.date fetched from to database (1-2 secs)
        timestamp = time.mktime(get_earliest_post_time(active_posts).timetuple()) - 10
        found_posts_ids = {}
        try:
            vk_posts = [p for p in crawler.get_posts_from_group("-" + gid, timestamp)]
        except FailedRequestError:
            print "failed to fetch posts for group " + str(gid)
            return
        for p in vk_posts:
            found_posts_ids[str(p['id'])] = p
        # cleansing
        posts_to_update = []
        for p in active_posts:
            if not p.pid in found_posts_ids:
                print "Deleting probably spam post " + p.pid
                p.delete()
            else:
                posts_to_update.append((p, found_posts_ids[p.pid]))
        try:
            comments_and_likes = crawler.get_comments_and_likes_for_posts([p[1] for p in posts_to_update], "-" + gid)
        except FailedRequestError:
            print "failed to fetch comments and likes for posts of group " + str(gid)
            return
        for (db_post, vk_post) in posts_to_update:
            comments = comments_and_likes[vk_post['id']]['comments']
            self.update_post(db_post, vk_post, comments)
            self.update_user_activity_for_post(db_post, comments, comments_and_likes[vk_post['id']]['likes'])                   
    
    def update_comments_for_post(self, post, source):
        if len(source) == 0:
            return       
        ids_table = self.add_non_existing_users_to_db([c['uid'] for c in source])
        all_saved_actions = {action.content_id for action in UserSocialAction.objects.filter(post=post, type="comment")}
        for c in source:
            if not str(c['cid']) in all_saved_actions:
                print "adding comment " + str(c["cid"])
                UserSocialAction.objects.create(post_id=post.id, user_id=ids_table[c['uid']], content_id=c['cid'], type="comment", date=datetime.fromtimestamp(c['date']))
    
    def update_likes_for_post(self, post, source):
        if len(source) == 0:
            return
        ids_table = self.add_non_existing_users_to_db([c for c in source])
        all_saved_actions = {action.user_id for action in UserSocialAction.objects.filter(post=post, type="like")}
        for c in source:
            if not ids_table[c] in all_saved_actions:
                print "adding like " + str(c)
                UserSocialAction.objects.create(post_id=post.id, user_id=ids_table[c], content_id="", type="like", date=datetime.now())        
    
    def add_non_existing_users_to_db(self, ids_list):
        users_set = list({int(user_id) for user_id in ids_list})
        users_count = len(users_set)
        in_db_users = {}
        loaded = 0
        while users_count > loaded:
            users_from_db = list(User.objects.filter(snid__in=users_set[loaded : loaded + settings.MAX_SQL_QUERY_SET_SIZE]))
            loaded += settings.MAX_SQL_QUERY_SET_SIZE
            for u in users_from_db:
                in_db_users[u.snid] = u.id
        for u in users_set:
            if not u in in_db_users:
                print "adding user " + str(u)
                new_user = User.objects.create(snid=u, last_scanned=datetime.now() - timedelta(days=365))
                in_db_users[u] = new_user.id          
        return in_db_users
         
    def update_user_activity_for_post(self, post, comments, likes):
        self.update_comments_for_post(post, comments)
        self.update_likes_for_post(post, likes)
            
    def update_post(self, post, post_fresh_vk_data, comments):
        now = datetime.now()
        print "Updating post " + str(post.pid)
        post.last_scanned = now
        min_time_comment = 10000000000
        max_time_comment = time.mktime(post.last_comment_date.timetuple())
        for c in comments:
            #print "comment found, date: " + str(datetime.fromtimestamp(c['date']))
            if c['date'] > max_time_comment:
                max_time_comment = c['date']
            if c['date'] < min_time_comment:
                min_time_comment = c['date']
        post.first_comment_date = post.first_comment_date if min_time_comment == 10000000000 else datetime.fromtimestamp(min_time_comment)
        post.last_comment_date = datetime.fromtimestamp(max_time_comment)
        if now - post.last_comment_date > timedelta(days=8):
            post.closed = True
            print "Closing post " + str(post.pid)
        for s in self._stats:
            obs = PostObservation(date=now, value=post_fresh_vk_data[s]['count'], post_id=post.id, statistics=s)
            obs.save()           
            latest_obs = list(LatestPostObservation.objects.filter(post=post, statistics=s))[0]
            latest_obs.value = post_fresh_vk_data[s]['count']
            latest_obs.save()
        post.save()
        