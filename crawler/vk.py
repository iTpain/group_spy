from math import ceil
from group_spy.utils.vk import VKRequest
from group_spy.logger.error import LogError
from threading import Thread

class OutOfCredentialsError(BaseException):
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
        request_maker = VKRequest (self._credentials)
        try:
            self.response = request_maker.blocking_request(self._req_dict)
        except LogError as e:
            self.response = None
            self.error = e

class VKCrawler(object):
    
    '''
    VK crawler is as simple as a piece of cake VK API client, relying on utils.vk.VKRequest class.
    all network activity is blocking.
    you should supply standard VK security tokens: api_id, viewer_id, session_id (sid), secret (contained in flashVars for Flash application). 
    '''
    
    _request_maker = None
    _count_per_load = 100
    _profiles_count_per_load = 400
    _credentials_list = None
    
    def __init__(self, credentials_list):
        self._credentials_list = credentials_list
        self._request_maker = VKRequest(credentials_list[0])
    
    def test_current_credentials(self):
        good_credentials = []
        for c in self._credentials_list:
            request = VKRequest(c)
            try:
                request.blocking_request({'method': 'getProfiles', 'uids': '1'})
                good_credentials.append(c)
            except LogError:
                pass
        return good_credentials
    
    def get_profiles(self, uids):
        return (user for user in self.set_generator({'method': 'getProfiles', 'fields': 'sex,photo,bdate,education,city'}, 'uids', uids))
    
    def get_cities(self, cids):
        return (city for city in self.set_generator({'method': 'places.getCityById'}, 'cids', cids))
               
    def get_groups(self, gids):
        return (group for group in self.set_generator({'method': 'groups.getById'}, 'gids', gids))       
                
    def get_group_members(self, gid):
        params = {'method': 'groups.getMembers', 'gid': gid}
        for member in self.generic_countable_objects_generator(params, lambda r: r['users'], lambda r: True, 1000):
            yield member
                
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
        for like in self.generic_countable_objects_generator (params, lambda r: r['users'], lambda like: True):
            yield like
    
    def get_jobs_done(self, reqs, creds):
        jobs = [GenericLoadJob(r, c) for r, c in zip(reqs, creds)]
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        for j in jobs:
            if j.response == None:
                raise j.error
        return [j.response for j in jobs]
    
    def set_generator(self, params, key, ids):
        loaded = 0
        while True:
            if loaded >= len(ids):
                break
            workers_count = len(self._credentials_list)
            prev_loaded = loaded
            req_dicts = []
            creds = []
            for i in xrange(workers_count):
                req_dict = {key: ",".join ([str(p) for p in ids[loaded + i * self._profiles_count_per_load : loaded + (i + 1) * self._profiles_count_per_load]])}
                if len(req_dict[key]) == 0:
                    break
                for p in params:
                    req_dict[p] = params[p]
                #print str(loaded + i * self._profiles_count_per_load) + " " + str(loaded + (i + 1) * self._profiles_count_per_load)
                req_dicts.append(req_dict)
                creds.append(self._credentials_list[i])
            try:  
                result = [response for response in self.get_jobs_done(req_dicts, creds)]
                loaded += workers_count * self._profiles_count_per_load
            except LogError as e:
                good_credentials = self.test_current_credentials()
                if len(good_credentials) == len(self._credentials_list):
                    raise e
                self._credentials_list = good_credentials
                if len(self._credentials_list) == 0:
                    raise LogError(OutOfCredentialsError())
                else:
                    print "Credentials failure in process, remaining good credentials count: " + str(len(self._credentials_list))
                    loaded = prev_loaded
                    continue  
            for r in result:
                for data_piece in r:
                    yield data_piece
    
    def generic_countable_objects_generator (self, request_params, fetch_array_func, filter_func, count = 0):
        offset = 0
        if count == 0:
            count = self._count_per_load
        while True:
            req_dicts = []
            prev_offset = offset
            for c in self._credentials_list:
                req_dict = {'offset': str (offset), 'count': str (count)}
                offset += count
                for p in request_params:
                    req_dict[p] = request_params[p]
                req_dicts.append(req_dict)    
            try:    
                responses = [fetch_array_func(r) for r in self.get_jobs_done(req_dicts, self._credentials_list)]
            except LogError as e:
                good_credentials = self.test_current_credentials()
                if len(good_credentials) == len(self._credentials_list):
                    raise e
                self._credentials_list = good_credentials
                if len(self._credentials_list) == 0:
                    raise LogError(OutOfCredentialsError())
                else:
                    print "Credentials failure in process, remaining good credentials count: " + str(len(self._credentials_list))
                    offset = prev_offset
                    continue
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