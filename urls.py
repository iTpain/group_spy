#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'crossdomain.xml', 'main_spy.views.crossdomainXML'),
    url(r'credentials/update/(?P<api_id>[A-Za-z0-9_]+)/(?P<viewer_id>[A-Za-z0-9_]+)/(?P<sid>[A-Za-z0-9_]+)/(?P<secret>[A-Za-z0-9_]+)/$', 'main_spy.views.receive_vk_credentials'),
    url(r'groups/$', 'main_spy.views.groups_main'),
    url(r'posts(?P<group_id>\d+)/$', 'main_spy.views.group_posts'),
    url(r'group(?P<group_id>\d+)/$', 'main_spy.views.group_status'),
    
    url(r'group(?P<group_id>\d+)/add/$', 'main_spy.crud_views.add_group'),
    url(r'group(?P<group_id>\d+)/delete/$', 'main_spy.crud_views.delete_group'),   
    url(r'group(?P<group_id>\d+)/update_info/$', 'main_spy.crud_views.update_group_info'),
    url(r'group(?P<group_id>\d+)/snapshot/$', 'main_spy.stat_views.get_group_current_stats'),
    url(r'group(?P<group_id>\d+)/intraday_stratify/(?P<time_start>[0-9]+)/(?P<time_end>[0-9]+)/$', 'main_spy.stat_views.get_social_activity_for_intraday_stratas'),
    url(r'group(?P<group_id>\d+)/intraweek_stratify/(?P<time_start>[0-9]+)/(?P<time_end>[0-9]+)/$', 'main_spy.stat_views.get_social_activity_for_intraweek_stratas'),
    url(r'group(?P<group_id>\d+)/content_stratify/(?P<time_start>[0-9]+)/(?P<time_end>[0-9]+)/$', 'main_spy.stat_views.get_social_activity_for_content_stratas'),   
    url(r'group(?P<group_id>\d+)/all_social_stats_snapshots/(?P<time_start>[0-9]+)/(?P<time_end>[0-9]+)/$', 'main_spy.stat_views.get_series_group_wide_all_social_stats'),
    url(r'group(?P<group_id>\d+)/all_user_stats_snapshots/(?P<time_start>[0-9]+)/(?P<time_end>[0-9]+)/$', 'main_spy.stat_views.get_series_group_wide_all_user_stats'),
    url(r'group(?P<group_id>\d+)/all_social_stats_finals/(?P<time_start>[0-9]+)/(?P<time_end>[0-9]+)/(?P<content_types>[a-z_,]*)/$', 'main_spy.stat_views.get_all_stats_series_for_posts'),
    url(r'group(?P<group_id>\d+)/latest_demogeo_snapshot/(?P<time>[0-9]+)/$', 'main_spy.stat_views.get_demogeo_snapshot'),
    
    url(r'group(?P<group_id>\d+)/posts/(?P<start>[0-9]+)/(?P<count>[0-9]+)/$', 'main_spy.crud_views.get_posts'),
    url(r'group(?P<group_id>\d+)/category/get_all/$', 'main_spy.crud_views.get_text_categories'),
    url(r'group(?P<group_id>\d+)/category/add/$', 'main_spy.crud_views.add_text_category'),
    url(r'text_category(?P<id>\d+)/update/$', 'main_spy.crud_views.update_text_category'),
    url(r'text_category(?P<id>\d+)/delete/$', 'main_spy.crud_views.remove_text_category'),
    url(r'text_category(?P<category_id>\d+)/assoc/(?P<post_id>\d+)/$', 'main_spy.crud_views.associate_text_category_with_post'),
    url(r'text_category(?P<category_id>\d+)/deassoc/(?P<post_id>\d+)/$', 'main_spy.crud_views.deassociate_text_category_with_post'),
    
    url(r'^admin/', include(admin.site.urls))
)
