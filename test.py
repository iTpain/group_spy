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

"""from main_spy.models import LatestDemogeoObservation
x = list(LatestDemogeoObservation.objects.all())
for y in x:
    print y
    print y.group_id
    print y.json
exit()"""

launch([UserScanner, PostsScanner, GroupScanner], [settings.USER_SCAN_INTERVAL, settings.POSTS_SCAN_INTERVAL, settings.GROUPS_SCAN_INTERVAL])
#launch([PostsScanner], [settings.POSTS_SCAN_INTERVAL])
#launch([GroupScanner], [settings.GROUPS_SCAN_INTERVAL])