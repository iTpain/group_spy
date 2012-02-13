from group_spy.main_spy.views_utils import json_response, request_vk_credentials
from group_spy.utils.misc import get_credentials
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from group_spy import settings
from group_spy.crawler.vk import VKCrawler
from group_spy.main_spy.models import Group

import time
from datetime import datetime, timedelta  

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
       
def group_status(request, group_id):
    return render_to_response ('group_status.html', {'group_id': group_id}, context_instance=RequestContext(request))

def group_posts(request, group_id):
    return render_to_response ('posts.html', {'group_id': group_id}, context_instance=RequestContext(request))

def groups_main(request):
    groups = Group.objects.all ()
    return render_to_response ('groups.html', {'groups': groups}, context_instance=RequestContext(request))
 