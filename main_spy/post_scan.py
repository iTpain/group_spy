from group_spy.main_spy.models import Post, Group, PostObservation, PostAttachment
from datetime import datetime, timedelta
import time
from group_spy.logger.error import LogError

def iso_date_from_ts(ts):
    return datetime.fromtimestamp(ts).isoformat(' ')

class PostsScanner(object):
    
    def scan(self, crawler):
        groups = Group.objects.all()
        for g in groups:
            print "Fetching new posts for group " + str(g.gid)
            try:
                self.find_new_posts(crawler, g.gid)
                self.update_group_posts(crawler, g.gid)
            except LogError:
                continue
        print "Posts scan completed"
        
    def find_new_posts(self, crawler, gid):
        #time.mktime((datetime.now() - timedelta(days=5)).timetuple())
        for p in crawler.get_posts_from_group("-" + str(gid)):
            try:
                Post.objects.get(pid=p['id'])
                break
            except Post.DoesNotExist:
                now = iso_date_from_ts(time.time())
                post_date = iso_date_from_ts(p['date'])
                new_post = Post(pid=p['id'], date=post_date, text=p['text'], last_scanned=now, closed=False, first_comment_date=now, last_comment_date=now, group_id=gid)
                print "Post " + str(p['id']) + " added, date published: " + post_date
                new_post.save()
                self.create_attachments_for_post (p, new_post)
                
    def create_attachments_for_post(self, vk_data, post):
        if 'attachments' in vk_data:
            for attachment in vk_data['attachments']:
                db_attachment = PostAttachment(post=post, attachment_type=attachment['type'])
                db_attachment.save()
                print "Attachment " + attachment["type"] + " added to post " + str(post.pid)
    
    def update_group_posts(self, crawler, gid):
        active_posts = list(Post.objects.filter(closed=False, group=gid))
        min_time = datetime.fromtimestamp(10000000000)
        for p in active_posts:
            if p.date < min_time:
                min_time = p.date
        
        timestamp = time.mktime(min_time.timetuple())
        for p in crawler.get_posts_from_group("-" + gid, timestamp):
            try:
                post = (po for po in active_posts if str(po.pid) == str(p['id'])).next()
                self.update_post (crawler, post, p)
            except StopIteration:
                continue
            
    def update_post(self, crawler, post, post_fresh_vk_data):
        now = iso_date_from_ts(time.time())
        print "Updating post " + str(post.pid)
        post.last_scanned = now
        min_time_comment = 10000000000
        max_time_comment = 0
        for c in crawler.get_comments_for_post(post.pid, "-" + str(post.group_id)):
            if c['date'] > max_time_comment:
                max_time_comment = c['date']
            if c['date'] < min_time_comment:
                min_time_comment = c['date']
        post.first_comment_date = datetime.fromtimestamp(min_time_comment)
        post.last_comment_date = datetime.fromtimestamp(max_time_comment)
        if datetime.now() - post.last_comment_date > timedelta(days=8):
            post.closed = True
            print "Closing post " + str(post.pid)
        else:
            stats = ['likes', 'reposts', 'comments']
            for s in stats:
                obs = PostObservation(date=now, value=post_fresh_vk_data[s]['count'], post_id=post.id, statistics=s)
                obs.save()           
        post.save()
        