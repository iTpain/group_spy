from group_spy.main_spy.models import GroupObservation, Group
from time import gmtime, strftime
from group_spy.logger.error import LogError
from datetime import datetime

class GroupScanner(object):
    
    BANNED_AVATARS = {"http://vkontakte.ru/images/deactivated_clo.png", "http://vkontakte.ru/images/deactivated_c.gif", "http://vk.com/images/deactivated_c.gif"}
    FACELESS_AVATARS = {"http://vkontakte.ru/images/question_a.gif", "http://vkontakte.ru/images/question_b.gif", "http://vkontakte.ru/images/question_c.gif", "http://vkontakte.ru/images/camera_a.gif", "http://vkontakte.ru/images/camera_b.gif", "http://vkontakte.ru/images/camera_c.gif"}
    
    def scan(self, crawler):
        groups = Group.objects.all ()
        self.gather_groups_info(crawler, [g.gid for g in groups])
        for g in groups:
            try:
                print "Scanning group " + g.gid
                result = self.scan_group(crawler, g.gid)
                self.write_observations(g, result)
                g.last_scanned = datetime.now()
                print "Group " + g.gid + " successfully scanned"
            except Exception as e:
                print e
                LogError(e, "Failed to scan and save results for group " + g.gid)
        
    
    def gather_groups_info(self, crawler, gids):
        try:
            for g in crawler.get_groups(gids):
                group = Group.objects.get(gid=g['gid'])
                group.alias = g['name']
                group.save()
        except Exception as e:
            LogError(e, "Failed to get groups info")
    
    def scan_group(self, crawler, gid):
        total_users = 0
        banned_users = 0
        faceless_users = 0    
        group_uids = [u for u in crawler.get_group_members(gid)]
        for p in crawler.get_profiles(group_uids):
            if p['photo'] in self.BANNED_AVATARS:
                banned_users += 1
            elif p['photo'] in self.FACELESS_AVATARS:
                faceless_users += 1
            total_users += 1
        return {'total_users': total_users, 'banned_users': banned_users, 'faceless_users': faceless_users}
    
    def write_observations(self, group, result):
        now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        for (k, v) in result.iteritems():
            obs = GroupObservation (group_id=group.gid, date=now, value=v, statistics=k)
            print str(k) + ": " + str(v)
            obs.save ()
        group.last_scanned = now
        group.save ()
        
        