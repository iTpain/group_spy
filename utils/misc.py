from group_spy import settings
from group_spy.crawler.vk import VKCrawler
from group_spy.logger.error import LogError
import json

def get_credentials():
    required_credentials= ['api_id', 'viewer_id', 'sid', 'secret']
    try:
        credentials_handle = open (settings.VK_CREDENTIALS_FILE_PATH, "r")
        credentials = json.load (credentials_handle)
        credentials_handle.close()
        if not isinstance(credentials, list):
            return None
        credentials_list = [c for c in credentials if isinstance(c, dict) and len([r for r in required_credentials if not r in c]) == 0]
        good_credentials_list = []
        for c in credentials_list:
            try:
                if VKCrawler([c]).test_current_credentials():
                    good_credentials_list.append(c)
            except LogError as e:
                print "Error while testing credentials " + str(e)
                continue        
        if len(good_credentials_list) == 0:
            return None
        else:
            return good_credentials_list
    except:
        return None
    
def get_vk_crawler():
    credentials = get_credentials ()
    print credentials
    if credentials == None:
        return None
    else:
        return VKCrawler(credentials)