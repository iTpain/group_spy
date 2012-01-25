from django.core.management import setup_environ
import imp

imp.find_module("settings")

import settings
setup_environ(settings)

from babysitter.daemon import multilaunch, launch
from group_spy.main_spy.group_scan import GroupScanner
from group_spy.main_spy.post_scan import PostsScanner
from group_spy.main_spy.views import get_series_for_posts
from datetime import datetime

#http://localhost:8000/series/group21977113/social_dynamics//reposts/1326791430/1327557922/
#past = datetime.now()
#get_series_for_posts(None, '21977113', 'reposts', '', '1326791430', '1327557922')
#print datetime.now() - past
#exit()

multilaunch([
    [GroupScanner, settings.GROUPS_SCAN_INTERVAL], 
    [PostsScanner, settings.POSTS_SCAN_INTERVAL]
])

from threading import Thread
import time

#def calculate():
#    print "YES"
#    return 2 + 2

#class proc(Thread):
#    
#    def __init__ (self):
#        self._target = calculate
#        Thread.__init__ (self, None, calculate, None)
#    
#    def run(self):
#        self.result = self._target ()
        

#thread = proc()
#thread.start()

#time.sleep(1)
#thread.join()
#print thread.result

#launch(GroupScanner, settings.GROUPS_SCAN_INTERVAL)

#[
#    {"secret": "e17a2862ee", "viewer_id": "85201601", "api_id": "2673575", "sid": "ee54bd35dff3b165f5e4701d56a6b36320947b8d5f8ab9b064c210ca312e98"},
#    {"secret": "9f3cf3c54c", "viewer_id": "142589876", "api_id": "2673575", "sid": "72d386b44c2e735f7b5c21722a9ac746bae2c20b5a2cad6291f1bea230fa8e"},
#    {"secret": "361f3b2ff1", "viewer_id": "53426", "api_id": "2673575", "sid": "d1423584d7399b843244bdea74affb4e2ee0c8217cad4c444f226789ddaabe"},
#    {"secret": "d6930f1f24", "viewer_id": "5286713", "api_id": "2673575", "sid": "9a9b27df9cc9bcd4b3dedc903764041972461f154c20cdcc4d79dfc9f3c9d1"}
#]