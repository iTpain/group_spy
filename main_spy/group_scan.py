from group_spy.main_spy.models import GroupObservation, Group, Post, LatestDemogeoObservation, LatestPostObservation
from datetime import datetime, timedelta
from django.db.models import Sum
from django.db import DatabaseError
from group_spy.crawler.vk import FailedRequestError
from group_spy.utils.misc import get_earliest_post_time
import json, time

AGE_STRATAS = [[0, 18], [19, 21], [22, 24], [25, 27], [28, 30], [31, 35], [36, 45], [46, 100]]

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
    
    @staticmethod
    def get_id():
        return 'group_scan'
    
    BANNED_AVATARS = {"http://vkontakte.ru/images/deactivated_clo.png", "http://vkontakte.ru/images/deactivated_c.gif", "http://vk.com/images/deactivated_c.gif"}
    FACELESS_AVATARS = {"http://vkontakte.ru/images/question_a.gif", "http://vkontakte.ru/images/question_b.gif", "http://vkontakte.ru/images/question_c.gif", "http://vkontakte.ru/images/camera_a.gif", "http://vkontakte.ru/images/camera_b.gif", "http://vkontakte.ru/images/camera_c.gif"}
    
    def scan(self, crawler):
        groups = Group.objects.all ()
        self.gather_groups_info(crawler, [g.gid for g in groups])
        for g in groups:
            if g.gid != "29887826":
                continue
            try:
                print "Scanning group " + g.gid
                now = datetime.now()
                print "Time now " + str(now)
                active_posts = list(Post.objects.filter(closed=False, group=g.gid, date__lte=now - timedelta(hours=12)))
                auditory_result = self.scan_auditory_activity(crawler, active_posts, g.gid)
                users_result = self.scan_group_users(crawler, g.gid)
                activity_result = compute_group_activity(active_posts)
                self.write_observations(g, dict(dict(users_result.items() + activity_result.items()).items() + auditory_result.items()))
            except (FailedRequestError, DatabaseError) as e:
                print "Something went wrong during scan of group " + str(g.gid) + ": " + str(e)
        
    def gather_groups_info(self, crawler, gids):
        try:
            for g in crawler.get_groups(gids):
                group = Group.objects.get(gid=g['gid'])
                group.alias = g['name']
                group.save()
        except Exception as e:
            print "failed to gather groups info: " + str(e)
    
    def scan_auditory_activity(self, crawler, active_posts, gid):
        uids = {}
        active_posts_ids = [p.pid for p in active_posts]
        min_time = time.mktime(get_earliest_post_time(active_posts).timetuple()) - 10
        vk_posts = [p for p in crawler.get_posts_from_group("-" + gid, min_time)]
        active_vk_posts = [p for p in vk_posts if str(p['id']) in active_posts_ids]
        comments_and_likes = crawler.get_comments_and_likes_for_posts(active_vk_posts, "-" + gid).values()
        comments_user_ids = [str(c['uid']) for sublist in comments_and_likes for c in sublist['comments']]
        likes_user_ids = [str(l) for sublist in comments_and_likes for l in sublist['likes']]
        total_ids = comments_user_ids + likes_user_ids
        for uid in total_ids:
            if not uid in uids:
                uids[uid] = 0
            uids[uid] += 1
        result = {'users_1': 0, 'users_3': 0}
        for uid in uids:
            if uids[uid] >= 3:
                result['users_3'] += 1
            result['users_1'] += 1
        try:
            self.analyze_demogeo(gid, [profile for profile in crawler.get_profiles([uid for uid in uids.keys()])], 'active', crawler)
        except (FailedRequestError, DatabaseError) as e:
            print "failed to analyze demogeo for active auditory of group " + str(gid) + ": " + str(e)
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
        try:
            self.analyze_demogeo(gid, profiles, 'entire', crawler)
        except (FailedRequestError, DatabaseError) as e:
            print "failed to analyze demogeo of group " + str(gid) + ": " + str(e)
        return {'total_users': total_users, 'banned_users': banned_users, 'faceless_users': faceless_users}
    
    def analyze_demogeo(self, gid, profiles, source_id, crawler):
        demo_json = self.analyze_demo(profiles, crawler)
        geo_json = self.analyze_geo(profiles, crawler)
        result = {'demo': demo_json, 'geo': geo_json}
        try:
            observation = LatestDemogeoObservation.objects.get(group=gid, source=source_id)
        except LatestDemogeoObservation.DoesNotExist:
            observation = LatestDemogeoObservation(group_id=gid, source=source_id)
        observation.json = json.dumps(result)
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
        for a in AGE_STRATAS:
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
        agesex_only_stratas = {str(strata[0]) + '-' + str(strata[1]) + ":" + gender: 0 for strata in AGE_STRATAS for gender in ('man', 'woman')}
        for p in profiles:
            age = self.get_age_strata(p)
            sex = self.get_sex_strata(p)
            if age != 'undefined':
                agesex_only_stratas[age + ":" + sex] += 1
            education = self.get_education_strata(p)
            final_strata = age + ":" + sex + ":" + education
            if not final_strata in stratas:
                stratas[final_strata] = 0
            stratas[final_strata] += 1
        print agesex_only_stratas
        return stratas        
        
    def write_observations(self, group, result):
        now = datetime.now()
        for (k, v) in result.iteritems():
            obs = GroupObservation(group_id=group.gid, date=now, value=v, statistics=k)
            print str(k) + ": " + str(v)
            obs.save ()
        group.last_scanned = now
        group.save () 
            