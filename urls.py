from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'group(?P<gid>\d+)/$', 'main_spy.views.group_status'),
    url(r'groups/$', 'main_spy.views.groups_main'),
    url(r'group(?P<group_id>\d+)/snapshot/$', 'main_spy.views.get_group_current_stats'),
    url(r'group(?P<group_id>\d+)/update_info/$', 'main_spy.views.update_group_info'),
    url(r'group/add/(?P<gid>\d+)/$', 'main_spy.views.add_group'),
    url(r'credentials/update/(?P<api_id>[A-Za-z0-9_]+)/(?P<viewer_id>[A-Za-z0-9_]+)/(?P<sid>[A-Za-z0-9_]+)/(?P<secret>[A-Za-z0-9_]+)/$', 'main_spy.views.receive_vk_credentials'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'crossdomain.xml', 'main_spy.views.crossdomainXML'),
    url(r'series/group(?P<group_id>\d+)/(?P<stat_id>[a-z_]+)/(?P<time_start>[0-9]+)/(?P<time_end>[0-9]+)/$', 'main_spy.views.get_series_group_wide'),
    url(r'series/group(?P<group_id>\d+)/active_post_stats/(?P<content_types>[a-z_]*)/(?P<stat_id>[a-z_]+)/(?P<time_start>[0-9]+)/(?P<time_end>[0-9]+)/$', 'main_spy.views.get_series_for_posts')
)
