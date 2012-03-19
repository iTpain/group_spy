#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management import setup_environ
import imp

imp.find_module("settings")

import settings
setup_environ(settings)

from babysitter.daemon import launch
from group_spy.main_spy.group_scan import GroupScanner
from group_spy.main_spy.post_scan import PostsScanner
from group_spy.main_spy.user_scan import UserScanner
from group_spy.main_spy.models import Post, LatestPostObservation, PostObservation, GroupObservation, Group, PostAttachment, User, UserSocialAction
from datetime import datetime
from threading import Thread

"""
past = datetime.now()
http://localhost:8000/series/group13643401/social_dynamics_all//1296385474/1327921474/
get_all_stats_series_for_posts(None, '13643401', '', '1296385474', '1327921474')
http://localhost:8000/group21977113/intraday_stratify/1325585275/1328177275/
get_social_activity_for_intraday_stratas(None, '21977113', '1325585275', '1328177275')
print "oook"
detmir - 31769636 adidas sport - 13643401
print datetime.now() - past
exit()
"""


from group_spy.crawler.vk import VKCrawler
from group_spy.utils.misc import get_vk_crawler
from group_spy.apps.user_slicer import slice_group_users

from group_spy.asset_cook import walk_directory_recursively, process_templates

#process_templates("c:/projects/group_spy/main_spy/templates", "c:/projects/group_spy/main_spy/static")
#exit()
"""
groups = [
28477986, 
21118635, 
5858244
,18099999
,7029945
,1719791
,460389
,23180464
,32535747
,29246653
,25346844
,28468381
,3807937
,26858816
,23378353]

for g in groups:
    print ""
    print ""
    print "Группа " + str(g)
    slice_group_users(str(g), 50000, 
    [{
        'key': 'country_name',
        'tree': {
            'op': 'eq',
            'arg1': {'op': 'v', 'arg1': 'Казахстан'},
            'arg2': {'op': 'x'}
        }
    }]                                    
    )
exit()
"""

"""
l = len(Post.objects.all())
c = 0
crawler = get_vk_crawler()
for g in Group.objects.all(): 
    posts = list(Post.objects.filter(group=g.gid))
    for p in crawler.get_posts_from_group("-" + g.gid):
        try:
            post = (pd for pd in posts if int(pd.pid) == p['id']).next()
            print p['from_id']
            print "-" + g.gid
            if p['from_id'] != -int(g.gid):
                try:
                    user = User.objects.get(snid=p['from_id'])
                except User.DoesNotExist:
                    print "user does not exist"
                    user = User(snid=p['from_id'])
                    user.save()
                post.author = user
                post.author_is_group = False
            else:
                post.author = None
                post.author_is_group = True
                print "group"
            post.save()
            c += 1
            print str(c) + "/" + str(l) + " " + str(100 * float(c) / l) + "%"
        except StopIteration:
            print "not found"
exit()
"""

#c1 = list(Post.objects.filter(author_is_group=False))
#c2 = list(Post.objects.filter(author_is_group=True))
#ids = [c.id for c in c1] + [c.id for c in c2]
#ids_dict = {id: True for id in ids}
#posts = [p.id for p in list(Post.objects.all())]

#c = 0
#for p in posts:
#    if not p in ids_dict:
#        print p
#        c += 1
#        Post.objects.get(pk=p).delete()
#exit()


launch([UserScanner, PostsScanner, GroupScanner], [settings.USER_SCAN_INTERVAL, settings.POSTS_SCAN_INTERVAL, settings.GROUPS_SCAN_INTERVAL])
#launch([PostsScanner], [settings.POSTS_SCAN_INTERVAL])
#launch([GroupScanner], [settings.GROUPS_SCAN_INTERVAL])