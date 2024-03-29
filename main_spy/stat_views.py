from group_spy.main_spy.models import GroupObservation, Post, PostAttachment, LatestPostObservation, LatestDemogeoObservation, UserSocialAction, PostObservation, DemoObservation
from group_spy.main_spy.group_scan import compute_group_activity
from group_spy.main_spy.views_utils import login_required_json_response
from group_spy.main_spy.group_scan import AGE_STRATAS
from datetime import datetime, timedelta
from django.db.models import Sum, Count
from math import ceil
import time, json, cPickle

def memoize(limit=None):
    cache_dict = {}
    cache_list = []
    def wrap(function):
        def memoize_wrapper(*args, **kwargs):
            key = cPickle.dumps((args, kwargs))
            try:
                cache_list.append(cache_list.pop(cache_list.index(key)))
            except ValueError:
                cache_dict[key] = function(*args, **kwargs)
                cache_list.append(key)
                if limit is not None and len(cache_list) > limit:
                    del cache_dict[cache_list.pop(0)]
            return cache_dict[key]
        return memoize_wrapper
    return wrap
    
def time_align_decorator(ts_index, te_index, modulo=3600*24, max_length=timedelta(days=2048)):
    def wrap(func):
        def align_time_value(value):
            value = int(value)
            aligned = value - (value % modulo)
            return datetime.fromtimestamp(aligned)
            
        def wrapper(*args, **kwargs):
            new_args = list(args)
            new_args[ts_index] = align_time_value(new_args[ts_index])
            new_args[te_index] = align_time_value(new_args[te_index])
            if new_args[te_index] - new_args[ts_index] > max_length:
                new_args[ts_index] = new_args[te_index] - max_length
            return func(*new_args, **kwargs)
        return wrapper
    return wrap

#
#    Extract series snapshots for likes, posts count, comments, active users, etc.
#

@login_required_json_response
def get_series_group_wide(request, group_id, stat_id, time_start, time_end):
    return get_series_group_wide_inner(group_id, stat_id, time_start, time_end)

@login_required_json_response
def get_series_group_wide_all_social_stats(request, group_id, time_start, time_end):
    return get_stats_set_group_wide(group_id, ['active_posts_count', 'active_posts_likes', 'active_posts_reposts', 'active_posts_comments'], time_start, time_end)

@login_required_json_response
def get_series_group_wide_all_user_stats(request, group_id, time_start, time_end):
    return get_stats_set_group_wide(group_id, ['total_users', 'banned_users', 'faceless_users', 'users_1', 'users_3'], time_start, time_end)  

def get_stats_set_group_wide(group_id, stats, time_start, time_end):
    return {s: get_series_group_wide_inner(group_id, s, time_start, time_end) for s in stats}

@time_align_decorator(ts_index=2, te_index=3)
@memoize(limit=2048)
def get_series_group_wide_inner(group_id, stat_id, time_start, time_end):
    all_objects = GroupObservation.objects.filter(group=group_id, statistics=stat_id)
    series = get_series_from(all_objects, time_start, time_end)
    return {'series': series}

def get_series_from(objects, time_start, time_end):
    #interval = time_end - time_start
    #quanta = choose_quanta(interval)
    return wholesale_extract(objects, timedelta(days=1), time_start, time_end)

def choose_quanta(interval):
    if interval > timedelta(days=365):
        return timedelta(days=3)
    elif interval > timedelta(days=90):
        return timedelta(days=1)
    elif interval > timedelta(days=30):
        return timedelta(hours=3)
    else:
        return timedelta(hours=1)
    
def choose_max_absolute_error(interval):
    if interval > timedelta(days=365):
        return timedelta(days=2)
    elif interval > timedelta(days=30):
        return timedelta(hours=12)
    else:
        return timedelta(hours=1)

def wholesale_extract(objects, quanta, time_start, time_end):
    print objects
    print time_start
    print time_end
    all_data = list(objects.filter(date__gte=time_start, date__lte=time_end))
    print all_data
    try:
        start_data = objects.filter(date__lte=time_start).latest("date")
        start_value = start_data.value
    except:
        start_value = 0
    data_len = len(all_data)
    if data_len < 2:
        return []
    current_time = time_start
    prepped_data = []
    last_index_greater = 0
    while current_time < time_end + quanta:
        if current_time > time_end:
            current_time = time_end
        for index in range(last_index_greater, data_len):
            if all_data[index].date >= current_time:
                break
        last_index_greater = index
        if last_index_greater == 0 and all_data[last_index_greater].date > current_time:
            value = start_value
        else:
            value = all_data[last_index_greater].value 
        if current_time == time_start or current_time == time_end:
            data_time = current_time
        else:
            data_time = all_data[last_index_greater].date
        prepped_data.append([1000 * time.mktime(data_time.timetuple()), value])
        current_time += quanta
    return prepped_data

def get_abs_seconds_diff(d1, d2):
    if d1 > d2:
        return (d1 - d2)
    else:
        return (d2 - d1)

#
#    Get group stats snapshot for current moment and some moments in past
#

@login_required_json_response
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

#
#    Get final values dynamics for posts' comments, likes, reposts
#

@login_required_json_response
def get_series_for_posts(request, group_id, stat_id, content_types, time_start, time_end):
    return get_series_for_posts_inner(group_id, stat_id, content_types, time_start, time_end)

@login_required_json_response
def get_all_stats_series_for_posts(request, group_id, content_types, time_start, time_end):
    stats = {'likes': [], 'comments': [], 'reposts': []}
    for k in stats.keys():
        stats[k] = get_series_for_posts_inner(group_id, k, content_types, time_start, time_end)
    return stats

@time_align_decorator(ts_index=3, te_index=4)
@memoize(limit=2048)
def get_series_for_posts_inner(group_id, stat_id, content_types, time_start, time_end):
    content_types = [c for c in content_types.split(",") if len(c) > 0 and c in ['no_attachment', 'photo', 'posted_photo', 'video', 'audio', 'doc', 'graffiti', 'link', 'note', 'app', 'poll', 'page']]
    quanta = timedelta(days=1)#choose_quanta(time_end - time_start)
    series = []
    posts = Post.objects.filter(group=group_id, last_comment_date__gte=time_start - timedelta(days=7), date__lte=time_end, author_is_group=True)
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
        posts_in_quanta = [p for p in posts if p.date <= current_time and p.last_comment_date + timedelta(days=7) >= current_time]
        stat = 0
        for p in posts_in_quanta:
            stat = stat + stats[p.id]
        series.append([1000 * time.mktime(current_time.timetuple()), stat, len(posts_in_quanta)])
        current_time += quanta
    return {'series': series}

#
#    Get posts' cumulative social data by stratas
#

@login_required_json_response
def get_social_activity_for_intraday_stratas(request, group_id, time_start, time_end):
    return get_social_activity_stratified_template_func(group_id, time_start, time_end, intraday_stratify)

@login_required_json_response
def get_social_activity_for_intraweek_stratas(request, group_id, time_start, time_end):
    return get_social_activity_stratified_template_func(group_id, time_start, time_end, intraweek_stratify)

@login_required_json_response
def get_social_activity_for_content_stratas(request, group_id, time_start, time_end):
    return get_social_activity_stratified_template_func(group_id, time_start, time_end, content_type_stratify)

@time_align_decorator(ts_index=1, te_index=2)
@memoize(limit=2048)
def get_social_activity_stratified_template_func(group_id, time_start, time_end, stratification):
    posts = get_posts_in_period(group_id, time_start, time_end)
    stratas = stratification(posts)
    return compute_activity_for_stratas(stratas)

def get_posts_in_period(group_id, time_start, time_end):
    return list(Post.objects.filter(group=group_id, date__lte=time_end, last_comment_date__gte=time_start - timedelta(days=7), author_is_group=True))

def compute_activity_for_stratas(stratas):
    posts_counts = {}
    for k, s in stratas.iteritems():
        stratas[k]['stats'] = compute_group_activity(s['posts'])
        posts_counts[k] = len(stratas[k]['posts'])
        del stratas[k]['posts']
    response = {}
    for k, s in stratas.iteritems():
        for stat, val in s['stats'].iteritems():
            if not stat in response:
                response[stat] = {'series': []}
            response[stat]['series'].append([k, val, posts_counts[k]])
    return response

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
    
#
#    Get latest demogeo observation
#    

@login_required_json_response
def get_demogeo_snapshot(request, group_id):
    entire = LatestDemogeoObservation.objects.get(group=group_id, source="entire")
    active = LatestDemogeoObservation.objects.get(group=group_id, source="active")
    return {'entire': json.loads(entire.json), 'active': json.loads(active.json)}

#
#    Get demographics series
#
       
@login_required_json_response
def get_demographics_series(request, group_id, time_start, time_end):
    sources = ['entire', 'active']
    return {source: get_demographics_series_by_source(group_id, source, time_start, time_end) for source in sources}

@time_align_decorator(ts_index=2, te_index=3)
@memoize(limit=2048)       
def get_demographics_series_by_source(group_id, source, time_start, time_end):
    genders = {"man": True, "woman": False}
    response = {}
    time_start = time_end - timedelta(days=2)
    for gender_label, is_man in genders.iteritems():
        response[gender_label] = {age[1]: age_gender_series(group_id, source, age[1], is_man, time_start, time_end) for age in AGE_STRATAS}
    return response

def age_gender_series(group_id, source, age, is_man, time_start, time_end):
    return wholesale_extract(DemoObservation.objects.filter(group=group_id, source=source, is_man=True, age_group=age), timedelta(days=1), time_start, time_end)

#
#    Cumulative statistics over period for posts count etc
#

@login_required_json_response
def get_group_cumulative_post_stats(request, group_id, time_start, time_end):  
    if time_end == '0':
        time_end = datetime.now()
    else:
        time_end = datetime.fromtimestamp(int(time_end))
    time_start = datetime.fromtimestamp(int(time_start))
    social_actions = LatestPostObservation.objects.filter(post__group=group_id, post__date__lte=time_end, post__last_comment_date__gte=time_start - timedelta(days=7))
    social_actions_count = social_actions.values("statistics").annotate(total_actions=Sum('value'))
    posts = Post.objects.filter(group=group_id, date__lte=time_end, last_comment_date__gte=time_start - timedelta(days=7))
    group_users_count = GroupObservation.objects.filter(group=group_id, statistics="total_users").latest("date").value
    days_count = (posts.latest("date").date - posts.order_by("date").latest("date").date).days
    response = {'posts_count': posts.count(), 'group_users_count': group_users_count, 'days_count': days_count }
    for stat in social_actions_count:
        response[stat['statistics']] = stat['total_actions']
    return response

#
#    Group users activity rating
#

@login_required_json_response
def get_users_top(request, group_id):
    comments = UserSocialAction.objects.filter(type="comment", post__group=group_id).values('user', 'user__first_name', 'user__last_name', 'user__snid').annotate(comments=Count('user'))[0:200]
    likes = UserSocialAction.objects.filter(type="like", post__group=group_id).values('user', 'user__first_name', 'user__last_name', 'user__snid').annotate(likes=Count('user'))[0:200]
    users = {}
    for c in comments:
        c['likes'] = 0
        if not c['user'] in users:
            users[c['user']] = c
    for l in likes:
        l['comments'] = 0
        if not l['user'] in users:
            users[l['user']] = l
        else:
            users[l['user']]['likes'] = l['likes']
    return users


#
#    Social actions distribution over day/week
#

@login_required_json_response
def get_social_actions_distribution(request, group_id, time_start, time_end, stat_id):
    return get_social_actions_distribution_inner(group_id, time_start, time_end, stat_id)

@time_align_decorator(ts_index=1, te_index=2)
@memoize(limit=2048)
def get_social_actions_distribution_inner(group_id, time_start, time_end, stat_id):
    active_posts = [p.id for p in list(Post.objects.filter(group=group_id, date__lte=time_end, date__gte=time_start))]
    latest_post_observations = []
    per_request = 200
    total_requests = (len(active_posts) / 200) + 1
    for i in xrange(total_requests):
        latest_post_observations.extend(list(LatestPostObservation.objects.filter(statistics=stat_id).filter(post__in=active_posts[i * per_request : (i + 1) * per_request])))
    latest_post_observations.sort(key=lambda obs: -obs.value)    
    chosen_ids = [p.post_id for p in latest_post_observations[0 : 100]]   
    observations = list(PostObservation.objects.filter(post__in=chosen_ids, statistics=stat_id))
    observations_by_post = {}   
    for obs in observations:
        if not obs.post_id in observations_by_post:
            observations_by_post[obs.post_id] = []
        observations_by_post[obs.post_id].append(obs)
    days = [[p, 0] for p in range(7)]
    hours = [[p, 0] for p in range(24)]
    for collection in observations_by_post.values():
        collection = [c for c in collection if c.value > 0]
        if len(collection) < 2:
            continue
        #intraweek
        cur_obs = collection[0]
        cur_day = cur_obs.date.day
        for obs in collection[1:]:
            if obs.date.day != cur_day:
                delta = obs.value - cur_obs.value
                diff = float((obs.date - cur_obs.date).total_seconds()) / (3600 * 24)
                total_days = ceil(diff)
                cur_date = cur_obs.date
                while cur_date <= obs.date:
                    days[cur_date.weekday()][1] += delta / total_days
                    cur_date += timedelta(hours=24)
                cur_day = obs.date.day
                cur_obs = obs
        #intraday
        for i in xrange(len(collection) - 1):
            obs1 = collection[i]
            obs2 = collection[i + 1]
            delta_value = obs2.value - obs1.value
            if delta_value < 0:
                continue
            d1 = obs1.date
            d2 = obs2.date
            delta_time = d2 - d1
            per_second = float(delta_value) / delta_time.total_seconds()
            next_d1 = d1 + timedelta(hours=1)
            closest_to_d1 = datetime(next_d1.year, next_d1.month, next_d1.day, next_d1.hour)
            if d2 < closest_to_d1:
                hours[d1.hour][1] += delta_value
                continue
            else:
                hours[d1.hour][1] += per_second * (closest_to_d1 - d1).total_seconds()
            closest_to_d2 = datetime(d2.year, d2.month, d2.day, d2.hour)
            hours[d2.hour][1] += per_second * (d2 - closest_to_d2).total_seconds()
            cur_date = closest_to_d1
            if closest_to_d2 - closest_to_d1 >= timedelta(hours=1):
                while cur_date < closest_to_d2:
                    hours[cur_date.hour][1] += 3600 * per_second
                    cur_date += timedelta(hours=1)
    return {'days': {'series': days}, 'hours': {'series': hours}}
    