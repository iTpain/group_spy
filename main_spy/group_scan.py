from group_spy.main_spy.models import GroupObservation, Group, Post, DemogeoGroupObservation, LatestPostObservation
from time import gmtime, strftime
from group_spy.logger.error import LogError
from datetime import datetime
from django.db.models import Sum
import json

def compute_group_activity(active_posts):
    stats = {"likes": 0, "comments": 0, "reposts": 0}
    response_stats = {"likes": "active_posts_likes", "comments": "active_posts_comments", "reposts": "active_posts_reposts"}
    for k, v in stats.iteritems():
        value = LatestPostObservation.objects.filter(post__in=[p.id for p in active_posts], statistics=k).aggregate(Sum('value'))['value__sum']
        if value != None:
            stats[k] += value
    mapped_stats = {}
    for k, v in stats.iteritems():
        mapped_stats[response_stats[k]] = v
    mapped_stats["active_posts_count"] = len(active_posts)  
    return mapped_stats

class GroupScanner(object):
    
    BANNED_AVATARS = {"http://vkontakte.ru/images/deactivated_clo.png", "http://vkontakte.ru/images/deactivated_c.gif", "http://vk.com/images/deactivated_c.gif"}
    FACELESS_AVATARS = {"http://vkontakte.ru/images/question_a.gif", "http://vkontakte.ru/images/question_b.gif", "http://vkontakte.ru/images/question_c.gif", "http://vkontakte.ru/images/camera_a.gif", "http://vkontakte.ru/images/camera_b.gif", "http://vkontakte.ru/images/camera_c.gif"}
    
    def scan(self, crawler):
        groups = Group.objects.all ()
        self.gather_groups_info(crawler, [g.gid for g in groups])
        for g in groups:
            try:
                print "Scanning group " + g.gid
                active_posts = list(Post.objects.filter(closed=False, group=g.gid))
                auditory_result = self.scan_auditory_activity(crawler, active_posts, g.gid)
                print "auditory activity scanned"
                users_result = self.scan_group_users(crawler, g.gid)
                print "users scanned"
                activity_result = compute_group_activity(active_posts)
                print "group activity scanned"
                self.write_observations(g, dict(dict(users_result.items() + activity_result.items()).items() + auditory_result.items()))
                print "observations written"
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
    
    def scan_auditory_activity(self, crawler, active_posts, gid):
        uids = {}
        for post in active_posts:
            comments_user_ids = [str(c['uid']) for c in crawler.get_comments_for_post(post.pid, "-" + str(post.group_id))]
            likes_user_ids = [str(l) for l in crawler.get_likes_for_object('post', "-" + str(post.group_id), post.pid, False)]
            total_ids = comments_user_ids + likes_user_ids
            for uid in total_ids:
                if not uid in uids:
                    uids[uid] = 0
                uids[uid] += 1
        #raise 7
        result = {'users_1': 0, 'users_3': 0}
        for uid in uids:
            if uids[uid] >= 3:
                result['users_3'] += 1
            result['users_1'] += 1
        self.analyze_demogeo(gid, [profile for profile in crawler.get_profiles([uid for uid in uids.keys()])], False, crawler)
        return result
        
    def scan_group_users(self, crawler, gid):
        total_users = 0
        banned_users = 0
        faceless_users = 0    
        group_uids = [u for u in crawler.get_group_members(gid)]
        profiles = []
        for p in crawler.get_profiles(group_uids):
            if p['photo'] in self.BANNED_AVATARS:
                banned_users += 1
            else:
                profiles.append(p)
            if p['photo'] in self.FACELESS_AVATARS:
                faceless_users += 1
            total_users += 1
            #print p
        print "analyzing demogeo"
        self.analyze_demogeo(gid, profiles, True, crawler)
        return {'total_users': total_users, 'banned_users': banned_users, 'faceless_users': faceless_users}
    
    def analyze_demogeo(self, gid, profiles, whole_group, crawler):
        demo_json = self.analyze_demo(profiles, crawler)
        geo_json = self.analyze_geo(profiles, crawler)
        observation = DemogeoGroupObservation(group_id=gid, json=json.dumps({'demo': demo_json, 'geo': geo_json}), whole_group=whole_group)
        observation.save()
    
    def get_optimal_cities_set(self, cities, min_threshold, max_threshold, step, crit_value):
        threshold = max_threshold
        while True:
            major_cities = [c for c in cities if c[1] > threshold and len(c[0]) > 0]
            total_major_sum = 0
            for c in major_cities:
                total_major_sum += c[1]
            if total_major_sum < crit_value and threshold > min_threshold:
                threshold -= step
                continue
            else:
                major_cities.append(['other', 1 - total_major_sum])
                major_cities.sort(key=lambda c: c[1])
                return major_cities
    
    def analyze_geo(self, profiles, crawler):
        cids_list = [p['city'] for p in profiles if 'city' in p]
        cids_dict = {}
        alias_dict = {}
        for c in cids_list:
            if not c in cids_dict:
                cids_dict[c] = 0
                alias_dict[c] = ''
            cids_dict[c] += 1
        for alias_info in crawler.get_cities([c for c in cids_dict.keys()]):
            alias_dict[alias_info['cid']] = alias_info['name']
        sum = 0
        cities = [c for c in cids_dict.items() if c[0] != '0'] 
        for c in cities:
            sum += c[1]
        for index, c in enumerate(cities):
            cities[index] = [alias_dict[c[0]], float(c[1]) / sum]
        major_cities = self.get_optimal_cities_set(cities, 0.01, 0.02, 0.01, 0.8)
        #print major_cities
        return major_cities        
    
    def get_age_strata(self, profile):
        if not 'bdate' in profile:
            return 'undefined'
        bdate_pieces = profile['bdate'].split(".")
        year = 0
        for p in bdate_pieces:
            if len(p) == 4:
                year = int(p)
                break
        if year == 0:
            return 'undefined'
        now = datetime.now().year
        age = now - year
        profile['computed_age'] = age
        age_stratas = [[0, 11], [12, 15], [16, 18], [19, 21], [22, 24], [25, 27], [28, 30], [31, 35], [36, 45], [46, 120]]
        for a in age_stratas:
            if age >= a[0] and age <= a[1]:
                return str(a[0]) + '-' + str(a[1])
        return 'undefined'
    
    def get_education_strata(self, profile):
        if 'university' in profile and not ('computed_age' in profile and profile['computed_age'] < 18):
            return 'higher'
        else:
            return 'other'
    
    def get_sex_strata(self, profile):
        if profile['sex'] == 1:
            return 'woman'
        else:
            return 'man'
    
    def analyze_demo(self, profiles, crawler):
        stratas = {}
        for p in profiles:
            age = self.get_age_strata(p)
            if age == 'undefined':
                continue
            sex = self.get_sex_strata(p)
            education = self.get_education_strata(p)
            final_strata = age + ":" + sex + ":" + education
            if not final_strata in stratas:
                stratas[final_strata] = 0
            stratas[final_strata] += 1
        return stratas        
        
    def write_observations(self, group, result):
        now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        for (k, v) in result.iteritems():
            obs = GroupObservation (group_id=group.gid, date=now, value=v, statistics=k)
            print str(k) + ": " + str(v)
            obs.save ()
        group.last_scanned = now
        group.save ()     