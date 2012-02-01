# малолеток с высшим - нахуй, прочекать перформанс стратифая на адидас ориджиналс, диаграмки для демогео, прочекать пустой город в демогео, адаптивный трешхолд в городах

from django.core.management import setup_environ
import imp

imp.find_module("settings")

import settings
setup_environ(settings)

from babysitter.daemon import launch
from group_spy.main_spy.group_scan import GroupScanner
from group_spy.main_spy.post_scan import PostsScanner
from group_spy.main_spy.views import get_series_for_posts, get_social_activity_for_intraday_stratas, get_all_stats_series_for_posts
from group_spy.main_spy.models import Post, LatestPostObservation, PostObservation, GroupObservation, Group, PostAttachment
from datetime import datetime


past = datetime.now()
#http://localhost:8000/series/group13643401/social_dynamics_all//1296385474/1327921474/
#get_all_stats_series_for_posts(None, '13643401', '', '1296385474', '1327921474')
#print "oook"
#detmir - 31769636 adidas sport - 13643401
#exit()

#http://localhost:8000/series/group21977113/social_dynamics//reposts/1326791430/1327557922/
#get_series_for_posts(None, '21977113', 'reposts', '', '1326791430', '1327557922')
#http://localhost:8000/group13643401/intraday_stratify/1325068941/1327660941/
#get_social_activity_for_intraday_stratas(None, '13643401', '1325068941', '1327660941')
#print datetime.now() - past
#exit()

#Post.objects.all().delete()
#GroupObservation.objects.all().delete()
#PostObservation.objects.all().delete()
#PostAttachment.objects.all().delete()
#LatestPostObservation.objects.all().delete()

launch([PostsScanner, GroupScanner], [settings.POSTS_SCAN_INTERVAL, settings.GROUPS_SCAN_INTERVAL])
#launch([GroupScanner], [settings.GROUPS_SCAN_INTERVAL])