from group_spy.main_spy.models import GroupObservation, Group, PostObservation, Post, PostAttachment
from group_spy.utils.misc import get_vk_crawler, get_credentials
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from group_spy import settings
from group_spy.crawler.vk import VKCrawler
import json
import time
from datetime import datetime, timedelta

# json response decorator
def json_response(func):
    def wrapper (*args, **kwargs):
        response = func (*args, **kwargs)
        if not ('errors' in response):
            response = {'response': response, 'errors': []}
        return HttpResponse (json.dumps (response), mimetype='application/json')
    return wrapper

# vk api credentials decorator
def request_vk_credentials(func):
    def wrapper (*args, **kwargs):
        crawler = get_vk_crawler ()
        if crawler == None:
            return {'errors': ['Unable to get vk api credentials']}
        else:
            kwargs['crawler'] = crawler;
        return func (*args, **kwargs)
    return wrapper    

def crossdomainXML(request):
    response = HttpResponse()
    response.write('<cross-domain-policy><allow-access-from domain="*"/></cross-domain-policy>')
    return response

@json_response
def receive_vk_credentials(request, api_id, secret, sid, viewer_id):
    file_path = settings.VK_CREDENTIALS_FILE_PATH
    try:
        credentials_file = open(file_path, "r")
        json_credentials = json.load(credentials_file)
        credentials_file.close()
    except:
        return {'errors': ["Unable to read credentials file"]}      
    arrived_credentials = {'api_id': api_id, 'secret': secret, 'sid': sid, 'viewer_id': viewer_id}
    if VKCrawler([arrived_credentials]).test_current_credentials():
        json_credentials.append(arrived_credentials)       
        try:
            credentials_file = open(file_path, "w")
            credentials_file.write(json.dumps(json_credentials))
            credentials_file.close()
        except:
            return {'errors': ["Failed to write credentials file"]}
        good_credentials = get_credentials()
        uniques_dict = {c['viewer_id']: c for c in good_credentials} 
        unique_credentials = [v for k, v in uniques_dict.iteritems()]
        try:
            credentials_file = open(file_path, "w")
            credentials_file.write(json.dumps(unique_credentials))
            credentials_file.close()
            return {"useful_credentials": len(unique_credentials)}
        except:
            return {'errors': ["Failed to save credentials file"]}
    else:
        return {'errors': ["Credentials test has failed"]}

def choose_quanta(interval):
    if interval > timedelta(days=365):
        return timedelta(days=30)
    elif interval > timedelta(days=30):
        return timedelta(days=1)
    else:
        return timedelta(hours=1)

def pointwise_extract(objects, quanta, time_start, time_end):
    current_time = time_start
    prepped_data = []
    while current_time <= time_end:
        obs = list(objects.filter(date__gte=current_time)[0:1])
        if len(obs) == 0:
            break
        else:
            prepped_data.append([1000 * time.mktime(obs[0].date.timetuple()), obs[0].value])
            current_time = obs[0].date + quanta
    return prepped_data


def wholesale_extract(objects, quanta, time_start, time_end):
    all_data = list(objects.filter(date__gte=time_start, date__lte=time_end))
    if len(all_data) == 0:
        return []
    current_time = time_start
    prepped_data = []
    for obs in all_data:
        if obs.date >= current_time:
            prepped_data.append([1000 * time.mktime(obs.date.timetuple()), obs.value])
            current_time = obs.date + quanta
    return prepped_data
    
    
def get_extraction_method_for_interval(interval, quanta):
    seconds_in_interval = interval.total_seconds()
    seconds_in_quanta = quanta.total_seconds()
    approximate_selects = seconds_in_interval / seconds_in_quanta
    approximate_observations = seconds_in_interval / timedelta(hours=1).total_seconds()
    if approximate_observations > 10 * approximate_selects:
        return pointwise_extract
    else:
        return wholesale_extract
    

def get_series_from(objects, time_start, time_end):
    interval = time_end - time_start
    quanta = choose_quanta(interval)
    method = get_extraction_method_for_interval(interval, quanta)
    return method(objects, quanta, time_start, time_end)
    
@json_response
def get_series_group_wide (request, group_id, stat_id, time_start, time_end):
    all_objects = GroupObservation.objects.filter(group=group_id, statistics=stat_id)
    series = get_series_from(all_objects, datetime.fromtimestamp(int(time_start)), datetime.fromtimestamp(int(time_end)))
    return {'series': series}

@json_response
def get_series_for_posts (request, group_id, stat_id, content_types, time_start, time_end):
    all_posts = Post.objects.filter(group=group_id, closed=False)
    if len(content_types) > 0:
        content_types = content_types.split(",")
        attachments = PostAttachment.objects.filter(post__in=[post.id for post in all_posts]).filter(attachment_type__in=content_types)
        posts_ids = {attachment.post_id: True for attachment in attachments}.values()
        print posts_ids
        raise 'x'
    return get_series_from(all_posts, time_start, time_end)

@json_response
def get_group_current_stats(request, group_id):
    stats = ["total_users", "faceless_users", "banned_users", "active_posts_count", "active_posts_likes", "active_posts_comments", "active_posts_reposts"]
    stats_data = {s: GroupObservation.objects.filter(statistics=s, group=group_id).latest("date").value for s in stats}
    return stats_data

@json_response
def update_group_info(request, group_id):
    group = Group.objects.get(gid=group_id)
    group.agency = request.POST['agency']
    group.brand = request.POST['brand']
    group.save()
    return {}
       
def group_status(request, gid):
    return render_to_response ('group_status.html', {'group_id': gid}, context_instance=RequestContext(request))

def groups_main(request):
    groups = Group.objects.all ()
    return render_to_response ('groups.html', {'groups': groups}, context_instance=RequestContext(request))

@json_response
@request_vk_credentials
def add_group(request, gid, crawler):
    try:
        obj = Group.objects.filter(gid=gid)
        if len(obj) > 0:
            return {'errors': ['group already added']}
        for g in crawler.get_groups([gid]):
            group_name = g['name']
        new_group = Group(gid=gid, alias=group_name)
        new_group.save()
        return {'gid': gid, 'alias': group_name}
    except:
        return {'errors': ['Failed to save group']}
    
    