from group_spy.main_spy.models import GroupObservation, Group, PostObservation, Post, PostAttachment, LatestPostObservation, DemogeoGroupObservation
from group_spy.utils.misc import get_vk_crawler, get_credentials
from group_spy.main_spy.group_scan import compute_group_activity
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
        unique_credentials = {c['viewer_id']: c for c in good_credentials}.values()
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
    
def choose_max_absolute_error(interval):
    if interval > timedelta(days=365):
        return timedelta(days=2)
    elif interval > timedelta(days=30):
        return timedelta(hours=12)
    else:
        return timedelta(hours=1)

def pointwise_extract(objects, quanta, time_start, time_end):
    current_time = time_start
    prepped_data = []
    first_intersection_flag = False
    while current_time <= time_end:
        obs = list(objects.filter(date__gte=current_time)[0:1])
        if len(obs) == 0:
            break
        else:
            prepped_data.append([1000 * time.mktime(obs[0].date.timetuple()), obs[0].value])
            current_time = obs[0].date + quanta
            if current_time > time_end and not first_intersection_flag:
                current_time = time_end
                first_intersection_flag = True
    try:
        latest = objects.filter(date__lte=current_time).latest("date")
        latest_time = 1000 * time.mktime(latest.date.timetuple())
        if len(prepped_data) == 0 or latest_time != prepped_data[len(prepped_data) - 1][0]:
            prepped_data.append([latest_time, latest.value])
    except:
        pass
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

def get_abs_seconds_diff(d1, d2):
    if d1 > d2:
        return (d1 - d2)
    else:
        return (d2 - d1)

def get_approximation_for_stat(objects, date, max_absolute_error):
    closest_values = []
    try:
        closest_after = objects.filter(date__gte=date)[0]
        closest_values.append({'date': closest_after.date, 'value': closest_after.value})
    except IndexError:
        pass
    try:
        closest_before = objects.filter(date__lte=date).order_by('-date')[0]
        closest_values.append({'date': closest_before.date, 'value': closest_before.value})
    except IndexError:
        pass
    valid_values = [v for v in closest_values if get_abs_seconds_diff(v['date'], date) < max_absolute_error]
    total_weight = 0
    if len(valid_values) == 0:
        return "undefined"
    for v in valid_values:
        v['weight'] = 1 - get_abs_seconds_diff(v['date'], date).total_seconds() / max_absolute_error.total_seconds()
        total_weight = total_weight + v['weight']
    final_value = 0
    for v in valid_values:
        v['weight'] = v['weight'] / total_weight
        final_value = final_value + v['value'] * v['weight']
    return final_value
       
       
def get_series_group_wide_inner(group_id, stat_id, time_start, time_end):
    all_objects = GroupObservation.objects.filter(group=group_id, statistics=stat_id)
    series = get_series_from(all_objects, datetime.fromtimestamp(int(time_start)), datetime.fromtimestamp(int(time_end)))
    return {'series': series}
       
@json_response
def get_series_group_wide(request, group_id, stat_id, time_start, time_end):
    return get_series_group_wide_inner(group_id, stat_id, time_start, time_end)

@json_response
def get_series_group_wide_all_social_stats(request, group_id, time_start, time_end):
    stats = {'active_posts_count': [], 'active_posts_likes': [], 'active_posts_reposts': [], 'active_posts_comments': []}
    for s in stats.keys():
        stats[s] = get_series_group_wide_inner(group_id, s, time_start, time_end)
    return stats
    

@json_response
def get_series_for_posts(request, group_id, stat_id, content_types, time_start, time_end):
    return get_series_for_posts_inner(group_id, stat_id, content_types, time_start, time_end)

def get_series_for_posts_inner(group_id, stat_id, content_types, time_start, time_end):
    time_start = datetime.fromtimestamp(int(time_start))
    time_end = datetime.fromtimestamp(int(time_end))
    content_types = [c for c in content_types.split(",") if len(c) > 0 and c in ['photo', 'posted_photo', 'video', 'audio', 'doc', 'graffiti', 'link', 'note', 'app', 'poll', 'page']]
    quanta = choose_quanta(time_end - time_start)
    series = []
    posts = Post.objects.filter(group=group_id, last_comment_date__gte=time_start, date__lte=time_end)
    if len(content_types) > 0:
        attachments = PostAttachment.objects.filter(post__in=[post.id for post in posts], attachment_type__in=content_types)
        posts_ids = {attachment.post_id: True for attachment in attachments}
        posts = [post for post in posts if post.id in posts_ids]
    latest_observations = LatestPostObservation.objects.filter(statistics=stat_id, post__in=posts)
    stats = {p.id: 0 for p in posts}
    for l in latest_observations:
        stats[l.post_id] = l.value 
    current_time = time_start
    while current_time <= time_end:
        posts_in_quanta = [p for p in posts if p.date <= current_time and p.last_comment_date >= current_time]
        stat = 0
        for p in posts_in_quanta:
            stat = stat + stats[p.id]
        series.append([1000 * time.mktime(current_time.timetuple()), stat, len(posts_in_quanta)])
        current_time += quanta
    return {'series': series}

@json_response
def get_all_stats_series_for_posts(request, group_id, content_types, time_start, time_end):
    stats = {'likes': [], 'comments': [], 'reposts': []}
    for k in stats.keys():
        stats[k] = get_series_for_posts_inner(group_id, k, content_types, time_start, time_end)
    return stats

def get_posts_in_period(group_id, time_start, time_end):
    return list(Post.objects.filter(group=group_id, date__lte=time_end, last_comment_date__gte=time_start))

def intraday_stratify(posts):
    stratas = {k: {'posts': [], 'stats': {}} for k in xrange(24)}
    for p in posts:
        stratas[p.date.hour]['posts'].append(p)
    return stratas

def intraweek_stratify(posts):
    stratas = {k: {'posts': [], 'stats': {}} for k in xrange(7)}
    for p in posts:
        stratas[p.date.weekday()]['posts'].append(p)
    return stratas

def content_type_stratify(posts):
    types = ['no_attachment', 'photo', 'posted_photo', 'video', 'audio', 'doc', 'graffiti', 'link', 'note', 'app', 'poll', 'page']
    stratas = {k: {"posts": [], "stats": {}} for k in types}
    for p in posts:
        attachments = list(PostAttachment.objects.filter(post=p.id))
        if attachments:
            for a in attachments:
                if not a.attachment_type in stratas:
                    stratas[a.attachment_type] = {'posts': [], 'stats': {}}
                stratas[a.attachment_type]['posts'].append(p)
        else:
            stratas["no_attachment"]['posts'].append(p)
    return stratas
        
def compute_activity_for_stratas(stratas):
    for k, s in stratas.iteritems():
        stratas[k]['stats'] = compute_group_activity(s['posts'])
        del stratas[k]['posts']
    return stratas

def get_social_activity_stratified_template_func(group_id, time_start, time_end, stratification):
    posts = get_posts_in_period(group_id, datetime.fromtimestamp(int(time_start)), datetime.fromtimestamp(int(time_end)))
    stratas = stratification(posts)
    return compute_activity_for_stratas(stratas)

@json_response
def get_social_activity_for_intraday_stratas(request, group_id, time_start, time_end):
    return get_social_activity_stratified_template_func(group_id, time_start, time_end, intraday_stratify)
    
@json_response
def get_social_activity_for_intraweek_stratas(request, group_id, time_start, time_end):
    return get_social_activity_stratified_template_func(group_id, time_start, time_end, intraweek_stratify)

@json_response
def get_social_activity_for_content_stratas(request, group_id, time_start, time_end):
    return get_social_activity_stratified_template_func(group_id, time_start, time_end, content_type_stratify)
    
@json_response
def get_group_current_stats(request, group_id):
    stats = ["total_users", "faceless_users", "banned_users", "active_posts_count", "active_posts_likes", "active_posts_comments", "active_posts_reposts", "users_1", "users_3"]
    stats_data = {}
    now = datetime.now()
    for s in stats:
        objects = GroupObservation.objects.filter(statistics=s, group=group_id)
        stats_data[s] = {}
        stats_data[s]['latest'] = GroupObservation.objects.filter(statistics=s, group=group_id).latest("date").value
        stats_data[s]['day_ago'] = get_approximation_for_stat(objects, now - timedelta(days=1), timedelta(hours=2))
        stats_data[s]['week_ago'] = get_approximation_for_stat(objects, now - timedelta(days=7), timedelta(hours=12))
        stats_data[s]['month_ago'] = get_approximation_for_stat(objects, now - timedelta(days=30), timedelta(days=1))
    return stats_data

def get_demogeo(group_id, time, whole_group):
    try:
        value = DemogeoGroupObservation.objects.filter(group=group_id, whole_group=whole_group, date__lte=time).latest("date").json
        return json.loads(value)
    except DemogeoGroupObservation.DoesNotExist:
        try:
            value = DemogeoGroupObservation.objects.filter(group=group_id, whole_group=whole_group, date__gte=time)[0].json
            return json.loads(value)
        except DemogeoGroupObservation.DoesNotExist:
            return None

@json_response
def get_demogeo_snapshot(request, group_id, time):
    time = datetime.fromtimestamp(int(time))
    return {'whole_group': get_demogeo(group_id, time, True), 'active_users': get_demogeo(group_id, time, False)}

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
    
    