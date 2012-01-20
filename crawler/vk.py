from math import ceil
from group_spy.utils.vk import VKRequest
from group_spy.logger.error import LogError
from threading import Thread

class GenericLoadJob(Thread):
    
    _req_dict = None
    _credentials = None
    response = None
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
        self._request_maker = VKRequest (credentials_list[0])
    
    def test_current_credentials(self):
        try:
            generator = self.get_groups([1])
            for g in generator:
                print g
            return True
        except LogError:
            return False
    
    def get_profiles(self, uids):
        return (user for user in self.set_generator({'method': 'getProfiles', 'fields': 'sex,photo'}, 'uids', uids))
                
    def get_groups(self, gids):
        return (group for group in self.set_generator({'method': 'groups.getById'}, 'gids', gids))
                
    def set_generator(self, params, key, ids):
        workers_count = len(self._credentials_list)
        chunk_per_load = self._profiles_count_per_load * workers_count
        for i in range(0, int(ceil((len(ids) + 0.0) / chunk_per_load))):
            jobs = []
            for index, c in enumerate(self._credentials_list):
                req_dict = {key: ",".join ([str(p) for p in ids[chunk_per_load * i + index * self._profiles_count_per_load : chunk_per_load * i + (index + 1) * self._profiles_count_per_load]])}
                if len(req_dict[key]) == 0:
                    continue
                for p in params:
                    req_dict[p] = params[p]
                job = GenericLoadJob(req_dict, c)
                print "starting g-job for " + str(chunk_per_load * i + index * self._profiles_count_per_load) + "-" + str(chunk_per_load * i + (index + 1) * self._profiles_count_per_load)
                job.start()
                jobs.append(job)
            for j in jobs:
                j.join()
            print "all g-jobs completed"
            for (r, error) in [(j.response, j.error) for j in jobs]:
                if r == None:
                    raise error
                for data_piece in r:
                    yield data_piece       
                
    def get_group_members(self, gid):
        params = {'method': 'groups.getMembers', 'gid': gid}
        for member in self.generic_countable_objects_generator(params, lambda r: r['users'], lambda r: True, 1000):
            yield member
            
                
    def get_posts_from_group(self, gid, from_time = 0):
        params = {'method': 'wall.get', 'owner_id': gid}
        for post in self.generic_countable_objects_generator(params, lambda r: r[1:], lambda post: post['date'] > from_time):
            yield post
            
    #def get_posts_by_id(self, ids):
    #    params = {'method': 'wall.getById'}
    #    fetched = 0
    #    fetch_per_request = 100
    #    idslen = len(ids)
    #    while fetched < idslen:
    #        params['posts'] = ",".join(ids[fetched:fetched + fetch_per_request])
    #        params['posts'] = "13643401_68367"
    #        vk_data = self._request_maker.blocking_request(params)
    #        print params['posts']
    #        print vk_data
    #        for p in vk_data:
    #            yield p
    #        fetched += fetch_per_request
            
    def get_comments_for_post(self, post_id, owner_id):
        params = {'method': 'wall.getComments', 'sort': 'desc', 'owner_id': owner_id, 'post_id': post_id}
        for comment in self.generic_countable_objects_generator(params, lambda r: r[1:], lambda comment: True):
            yield comment
    
    def get_likes_for_object(self, like_object_type, owner_id, object_id, uberlikes_only):
        like_filter = "copies" if uberlikes_only else "likes"
        params = {'method': 'likes.getList', 'type': like_object_type, 'owner_id': owner_id, 'item_id': object_id, 'filter': like_filter}
        for like in self.generic_countable_objects_generator (params, lambda r: r['users'], lambda like: True):
            yield like
    
    def generic_countable_objects_generator (self, request_params, fetch_array_func, filter_func, count = 0):
        offset = 0
        if count == 0:
            count = self._count_per_load
        while True:
            jobs = []
            for c in self._credentials_list:
                req_dict = {'offset': str (offset), 'count': str (count)}
                offset += count
                for p in request_params:
                    req_dict[p] = request_params[p]
                print "starting job for " + str(offset) + "-" + str(offset + count)
                job = GenericLoadJob(req_dict, c)
                job.start()
                jobs.append (job)
            for j in jobs:
                j.join()
                #print "result for job: " + str(j.response)
            for j in jobs:
                if j.response == None:
                    raise j.error
            responses = [fetch_array_func(j.response) for j in jobs]
            finished_flag = False
            for r in responses:
                if not isinstance(r, list) or len(r) <= 1:
                    finished_flag = True
                else:
                    for post in r:
                        if filter_func (post):
                            yield post
                        else:
                            finished_flag = True
                            continue
            if finished_flag:
                return        
                
                

        