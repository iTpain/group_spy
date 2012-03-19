from group_spy import settings
from group_spy.crawler.vk import VKCrawler
from group_spy.logger.error import LogError
import json, re, fileinput
from datetime import datetime

def get_earliest_post_time(posts):
    min_time = datetime.fromtimestamp(10000000000)
    for p in posts:
        if p.date < min_time:
            min_time = p.date
    return min_time
    

def get_credentials():
    required_credentials= ['api_id', 'viewer_id', 'sid', 'secret']
    try:
        credentials_handle = open (settings.VK_CREDENTIALS_FILE_PATH, "r")
        credentials = json.load (credentials_handle)
        credentials_handle.close()
        if not isinstance(credentials, list):
            return None
        credentials_list = [c for c in credentials if isinstance(c, dict) and len([r for r in required_credentials if not r in c]) == 0]
        good_credentials_list = VKCrawler(credentials_list).test_current_credentials()     
        #print good_credentials_list
        if len(good_credentials_list) == 0:
            return None
        else:
            return good_credentials_list
    except:
        return None
    
def get_vk_crawler():
    credentials = get_credentials ()
    if credentials == None:
        return None
    else:
        return VKCrawler(credentials)

def list_to_quantity_dict(qlist):
    qdict = {}
    for l in qlist:
        if not l in qdict:
            qdict[l] = 0
        qdict[l] += 1
    return qdict

def sqlite_dump_to_mysql_dump():
    for line in fileinput.input():
        process = False
        for nope in ('BEGIN TRANSACTION','COMMIT', 'sqlite_sequence','CREATE UNIQUE INDEX'):
            if nope in line: break
        else:
            process = True
        if not process: 
            continue
        m = re.search('CREATE TABLE "([a-z_]*)"(.*)', line)
        if m:
            name, sub = m.groups()
            line = '''DROP TABLE IF EXISTS %(name)s;CREATE TABLE IF NOT EXISTS %(name)s%(sub)s'''
            line = line % dict(name=name, sub=sub)
        else:
            m = re.search('INSERT INTO "([a-z_]*)"(.*)', line)
            if m:
                line = 'INSERT INTO %s%s\n' % m.groups()
                line = line.replace('"', r'\"')
                line = line.replace('"', "'")
        line = re.sub(r"([^'])'t'(.)", r"\1THIS_IS_TRUE\2", line)
        line = line.replace('THIS_IS_TRUE', '1')
        line = re.sub(r"([^'])'f'(.)", r"\1THIS_IS_FALSE\2", line)
        line = line.replace('THIS_IS_FALSE', '0')
        line = line.replace('AUTOINCREMENT', 'AUTO_INCREMENT')
        print line