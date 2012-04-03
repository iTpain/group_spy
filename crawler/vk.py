from math import ceil
from group_spy.utils.vk import VKCredentials, InvalidCredentialsError
from group_spy.logger.error import LogError
from threading import Thread

class FailedRequestError(Exception):
    pass

class GenericLoadJob(Thread):
    
    _req_dict = None
    _credentials = None
    response = None
    has_run = False
    error = None
    
    def __init__(self, req_dict, credentials):
        self._req_dict = req_dict
        self._credentials = credentials
        self._target = self.do_job
        Thread.__init__(self)
        
    def run(self):
        self._target()
    
    def do_job(self):
        try:
            self.response = self._credentials.blocking_request(self._req_dict)
        except Exception as e:
            self.response = None
            self.error = e

class VKCrawler(object):
    
    '''
    VK crawler is as simple as a piece of cake VK API client, relying on utils.vk.VKRequest class.
    all network activity is blocking.
    you should supply standard VK security tokens: api_id, viewer_id, session_id (sid), secret (contained in flashVars for Flash application). 
    '''

    _count_per_load = 100
    _profiles_count_per_load = 400
    _credentials_list = None
    
    def __init__(self, credentials_list):
        self._credentials_list = credentials_list
    
    def get_profiles(self, uids):
        return (user for user in self.set_generator({'method': 'getProfiles', 'fields': 'sex,photo,bdate,education,city,country'}, 'uids', uids))
    
    def get_cities(self, cids):
        return (city for city in self.set_generator({'method': 'places.getCityById'}, 'cids', cids))
    
    def get_countries(self, cids):
        return (city for city in self.set_generator({'method': 'places.getCountryById'}, 'cids', cids))
               
    def get_groups(self, gids):
        return (group for group in self.set_generator({'method': 'groups.getById'}, 'gids', gids))       
    
    def get_group_members_count(self, gid):
        credentials = self._credentials_list.get_credentials()[0]
        response = credentials.blocking_request({'method': 'groups.getMembers', 'gid': gid, 'offset': 0, 'count': 1})
        return response['count']
              
    def get_group_members(self, gid, initial_offset = 0, max_number_to_return = 1000000000):
        params = {'method': 'groups.getMembers', 'gid': gid}
        already_returned = 0
        for member in self.generic_countable_objects_generator(params, lambda r: r['users'], lambda r: True, 1000, initial_offset):
            if already_returned < max_number_to_return:
                already_returned += 1
                yield member
            else:
                return
                
    def get_posts_from_group(self, gid, from_time = 0):
        params = {'method': 'wall.get', 'owner_id': gid}
        for post in self.generic_countable_objects_generator(params, lambda r: r[1:], lambda post: post['date'] >= from_time):
            yield post
            
    def get_comments_for_post(self, post_id, owner_id):
        params = {'method': 'wall.getComments', 'sort': 'desc', 'owner_id': owner_id, 'post_id': post_id}
        for comment in self.generic_countable_objects_generator(params, lambda r: r[1:], lambda comment: True):
            yield comment
    
    def get_likes_for_object(self, like_object_type, owner_id, object_id, uberlikes_only):
        like_filter = "copies" if uberlikes_only else "likes"
        params = {'method': 'likes.getList', 'type': like_object_type, 'owner_id': owner_id, 'item_id': object_id, 'filter': like_filter}
        for like in self.generic_countable_objects_generator(params, lambda r: r['users'], lambda like: True, 1000):
            yield like
    
    def get_comments_and_likes_for_posts(self, posts, owner_id):
        tasks = []
        max_likes = 1000
        max_comments = 100
        total_result = {}
        for p in posts:
            if p['id'] in total_result:
                continue
            total_result[p['id']] = {'likes': [], 'comments': []}
            comments_count = p['comments']['count']
            likes_count = p['likes']['count']
            comments_tasks = int(ceil(float(comments_count) / max_comments))
            likes_tasks = int(ceil(float(likes_count) / max_likes))
            for i in xrange(likes_tasks):
                tasks.append({'count': max_likes, 'offset': i * max_likes, 'method': 'likes.getList', 'type': 'post', 'owner_id': owner_id, 'item_id': p['id'], 'filter': 'likes'})
            for i in xrange(comments_tasks):
                tasks.append({'count': max_comments, 'offset': i * max_comments, 'method': 'wall.getComments', 'sort': 'desc', 'owner_id': owner_id, 'post_id': p['id']})
        completed = 0
        while completed < len(tasks):
            print str(completed) + "/" + str(len(tasks))
            credentials = self._credentials_list.get_credentials()
            if len(credentials) == 0:
                raise FailedRequestError()
            jobs = []
            counter = 0
            for i in xrange(len(credentials)):
                if completed + i >= len(tasks):
                    break
                jobs.append((tasks[completed + i], credentials[i]))
            result = self.get_jobs_done(jobs)
            if self.check_responses(result):
                for r in result:
                    req_data = r[2]
                    if req_data['method'] == 'likes.getList':
                        total_result[req_data['item_id']]['likes'].extend(r[0]['users'])  
                    else:
                        total_result[req_data['post_id']]['comments'].extend(r[0][1: ])  
                completed += len(result)
            else:
                continue
        return total_result

    def get_jobs_done(self, input):
        jobs = [GenericLoadJob(r, c) for r, c in input]
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        return [(j.response, j.error, j._req_dict) for j in jobs]
    
    def check_responses(self, responses):
        good_responses = [r for r in responses if r[0] != None]
        bad_credentials = [r for r in responses if isinstance(r[1], InvalidCredentialsError)]
        if len(good_responses) == len(responses):
            return True
        else:
            if len(good_responses) == 0 and len(bad_credentials) == 0:
                raise FailedRequestError()
            return False
    
    def set_generator(self, params, key, ids):
        loaded = 0
        while True:
            if loaded >= len(ids):
                break
            credentials = self._credentials_list.get_credentials()
            if len(credentials) == 0:
                raise FailedRequestError()
            workers_count = len(credentials)
            prev_loaded = loaded
            job_input = []
            for i in xrange(workers_count):
                req_dict = {key: ",".join ([str(p) for p in ids[loaded + i * self._profiles_count_per_load : loaded + (i + 1) * self._profiles_count_per_load]])}
                if len(req_dict[key]) == 0:
                    break
                for p in params:
                    req_dict[p] = params[p]
                job_input.append((req_dict, credentials[i]))
            result = self.get_jobs_done(job_input)
            if self.check_responses(result):
                loaded += workers_count * self._profiles_count_per_load
                for r in result:
                    for data_piece in r[0]:
                        yield data_piece
            else:
                continue  

    def generic_countable_objects_generator (self, request_params, fetch_array_func, filter_func, count = 0, initial_offset = 0):
        offset = initial_offset
        if count == 0:
            count = self._count_per_load
        while True:
            prev_offset = offset
            credentials = self._credentials_list.get_credentials()
            job_input = []
            if len(credentials) == 0:
                raise FailedRequestError()
            for c in credentials:
                req_dict = {'offset': str (offset), 'count': str (count)}
                offset += count
                for p in request_params:
                    req_dict[p] = request_params[p]
                job_input.append((req_dict, c))
            result = self.get_jobs_done(job_input)
            if self.check_responses(result):
                responses = [fetch_array_func(r[0]) for r in result]
                finished_flag = False
                for r in responses:
                    if not isinstance(r, list) or len(r) == 0:
                        finished_flag = True
                    else:
                        for post in r:
                            if filter_func(post):
                                yield post
                            else:
                                finished_flag = True
                                continue
                if finished_flag:
                    return 
            else:
                offset = prev_offset
                continue 