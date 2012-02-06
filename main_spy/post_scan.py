from group_spy.main_spy.models import Post, Group, PostObservation, PostAttachment, LatestPostObservation, VKUser, VKUserSocialAction
from datetime import datetime, timedelta
import time
from group_spy.logger.error import LogError
from group_spy.utils.misc import list_to_quantity_dict

def iso_date_from_ts(ts):
    return datetime.fromtimestamp(ts).isoformat(' ')

class PostsScanner(object):
    
    _stats = ['likes', 'reposts', 'comments']
    
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
        for p in crawler.get_posts_from_group("-" + str(gid)):
            try:
                Post.objects.get(pid=p['id'], group=gid)
                break
            except Post.DoesNotExist:
                now = iso_date_from_ts(time.time())
                post_date = iso_date_from_ts(p['date'])
                new_post = Post(pid=p['id'], date=post_date, text=p['text'], last_scanned=now, closed=False, first_comment_date=post_date, last_comment_date=post_date, group_id=gid)
                print "Post " + str(p['id']) + " added, date published: " + post_date
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
        min_time = datetime.fromtimestamp(10000000000)
        for p in active_posts:
            if p.date < min_time:
                min_time = p.date
        
        timestamp = time.mktime(min_time.timetuple())
        for p in crawler.get_posts_from_group("-" + gid, timestamp):
            try:
                post = (po for po in active_posts if str(po.pid) == str(p['id'])).next()
                post_comments = [c for c in crawler.get_comments_for_post(post.pid, "-" + str(post.group_id))]
                self.update_post(crawler, post, p, post_comments)
                #self.update_user_activity_for_post(crawler, post, post_comments)
            except StopIteration:
                continue
    
    def update_user_activity_param_for_post(self, crawler, post, source, param_id):
        users_dict = list_to_quantity_dict(source)
        vk_to_db = {}
        in_db_users_dict = {u.vkid: u.id for u in VKUser.objects.filter(vkid__in=users_dict.keys())}
        for uid in users_dict.keys():
            if not uid in in_db_users_dict:
                user = VKUser(vkid=uid, last_scanned=datetime(2000, 1, 1))
                user.save()
                vk_to_db[uid] = user.id
            else:
                vk_to_db[uid] = in_db_users_dict[uid]       
        social_actions = VKUserSocialAction.objects.filter(post=post, user__in=users_dict.keys())
        social_actions_dict = {sa.user_id: sa for sa in social_actions}
        for vk_id, db_id in vk_to_db.iteritems():
            if not db_id in social_actions_dict:
                kwargs = {'post': post, 'user_id': db_id, param_id: users_dict[vk_id]}
                action = VKUserSocialAction(**kwargs)
                action.save()
            if getattr(social_actions_dict[db_id], param_id) != users_dict[vk_id]:
                setattr(social_actions_dict[db_id], param_id, users_dict[vk_id])
                social_actions_dict[db_id].save()
                
    def update_user_activity_for_post(self, crawler, post, post_comments):
        self.update_user_activity_param_for_post(crawler, post, post_comments, "comments")
        self.update_user_activity_param_for_post(crawler, post, [like for like in crawler.get_likes_for_object('post', "-" + str(post.group_id), post.pid, False)], "likes")
            
    def update_post(self, crawler, post, post_fresh_vk_data, comments):
        now = iso_date_from_ts(time.time())
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
        if datetime.now() - post.last_comment_date > timedelta(days=8):
            post.closed = True
            print "Closing post " + str(post.pid)
        for s in self._stats:
            obs = PostObservation(date=now, value=post_fresh_vk_data[s]['count'], post_id=post.id, statistics=s)
            obs.save()           
            latest_obs = list(LatestPostObservation.objects.filter(post=post, statistics=s))[0]
            latest_obs.value = post_fresh_vk_data[s]['count']
            latest_obs.save()
        post.save()
        