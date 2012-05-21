from group_spy.main_spy.models import Post, Group, PostObservation, PostAttachment, LatestPostObservation, User, UserSocialAction
from datetime import datetime, timedelta
from group_spy.logger.error import LogError

class UserScanner(object):
    
    @staticmethod
    def get_id():
        return 'user scan'
    
    def scan(self, crawler):
        now = datetime.now()
        users_to_scan = User.objects.filter(last_scanned__lte=now - timedelta(days=60))[0:5000]
        user_ids = [u.snid for u in users_to_scan]
        user_dict = {u.snid: u for u in users_to_scan}
        try:
            for profile in crawler.get_profiles(user_ids):
                user = user_dict[profile['uid']]
                user.first_name = profile['first_name']
                user.last_name = profile['last_name']
                user.last_scanned = now
                user.save()
                print "saving %s" % profile['uid']
        except LogError:
            pass
            
        