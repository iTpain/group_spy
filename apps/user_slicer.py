from group_spy.utils.misc import get_vk_crawler, get_credentials
from group_spy.utils.vk import is_user_banned, augment_profiles_with_extended_geo_info, augment_profiles_with_extended_age_info
from group_spy.crawler.vk import VKCrawler
from math import ceil
from random import shuffle
from datetime import datetime
from threading import Thread

class GroupMembersJob(Thread):

    response = None
    
    def __init__(self, credentials, group_id, offset, count):
        self._group_id = group_id
        self._crawler = VKCrawler([credentials])
        self._target = self.do_job
        self._offset = offset
        self._count = count
        Thread.__init__(self)
        
    def run(self):
        self._target()
    
    def do_job(self):
        self.response = list(self._crawler.get_group_members(self._group_id, self._offset, self._count))


def slice_group_users(group_id, samples_count, filter_json_schema):
    BLOCK_SIZE = 1000.0
    credentials = get_credentials()
    members_count = VKCrawler([credentials[0]]).get_group_members_count(group_id)
    total_blocks = ceil(members_count / BLOCK_SIZE)
    blocks_for_samples = int(min(total_blocks, ceil(samples_count) / BLOCK_SIZE))
    ordered_blocks = range(int(total_blocks))
    shuffle(ordered_blocks)
    blocks_to_fetch = ordered_blocks[0:blocks_for_samples]

    past = datetime.now()
    fetched = 0
    ids = []
    while fetched < len(blocks_to_fetch):
        jobs = []
        for c in credentials:
            jobs.append(GroupMembersJob(c, group_id, BLOCK_SIZE * blocks_to_fetch[fetched], BLOCK_SIZE))
            fetched += 1
            if fetched >= len(blocks_to_fetch):
                break
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        for response in [j.response for j in jobs]:
            ids.append(response)   
    ids = [item for sublist in ids for item in sublist]
    #print "ids received in: " + str(datetime.now() - past)
    
    
    past = datetime.now()
    crawler = VKCrawler(credentials)
    profiles = [p for p in crawler.get_profiles(ids) if not is_user_banned(p)]
    #print "profiles received in: " + str(datetime.now() - past)
    
    augment_profiles_with_extended_geo_info(crawler, profiles)
    augment_profiles_with_extended_age_info(profiles)
    filtered_profiles = filter_profiles_by_json_schema(profiles, filter_json_schema, members_count)
    
    ages = {}
    for p in filtered_profiles:
        if 'age' in p:
            if not p['age'] in ages:
                ages[p['age']] = 0
            ages[p['age']] += 1
    intervals = [[11, 0], [15, 0], [18, 0], [21, 0], [24, 0], [27, 0], [30, 0], [35, 0], [45, 0], [120, 0]]
    for age, count in ages.iteritems():
        for i in intervals:
            if age < i[0]:
                i[1] += count
                break
    sum = 0
    for i in intervals:
        sum += i[1]
    percentages = [100 * float(i[1]) / sum for i in intervals]
    cur_age = 0
    for i in xrange(len(intervals)):
        print str(cur_age) + "-" + str(intervals[i][0]) + ": " + str(percentages[i]) + "%"
        cur_age = intervals[i][0] + 1

def filter_profiles_by_json_schema(profiles, schema, members_count):
    if schema == None:
        return profiles
    filtered = []
    qualified_profiles = 0
    for p in profiles:
        profile_ok = True
        profile_qualified = True
        for filter_field in schema:
            key = filter_field['key']
            values_tree = filter_field['tree']
            if not key in p:
                profile_qualified = False
                break
            if not execute_operation_for_node(p[key], values_tree):
                profile_ok = False
        if profile_qualified:
            qualified_profiles += 1
            if profile_ok:
                filtered.append(p)
    #print len(profiles)
    #print qualified_profiles
    #print len(filtered)
    print "Users count:" + str(int(members_count * len(filtered) / float(qualified_profiles))) + " " + str(100 * float(len(filtered)) / qualified_profiles) + "%"
    print ""
    return filtered

class UnsupportedOperationError(BaseException):
    pass    

def execute_operation_for_node(value, tree):
    operation = tree['op']
    argument1 = tree['arg1'] if 'arg1' in tree else None
    argument2 = tree['arg2'] if 'arg2' in tree else None
    if operation == "x":
        return value
    elif operation == "v":
        return argument1
    elif operation == "eq":
        return execute_operation_for_node(value, argument1) == execute_operation_for_node(value, argument2)
    else:
        raise UnsupportedOperationError()