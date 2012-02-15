#!/usr/bin/env python
# -*- coding: utf-8 -*-

from group_spy.main_spy.views_utils import json_response, request_vk_credentials
from group_spy.utils.misc import get_credentials
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from group_spy import settings
from group_spy.crawler.vk import VKCrawler
from group_spy.main_spy.models import Group, ScanStats, GroupObservation, Post
from django.db.models import Avg
import group_spy.settings
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
    
    scanner_labels = ["Группы", "Посты"]
    scanner_classes = ["group_scan", "post_scan"]
    scanner_intervals = [settings.GROUPS_SCAN_INTERVAL, settings.POSTS_SCAN_INTERVAL]
    scanner_times = [ScanStats.objects.filter(scanner_class=sc).order_by("-date")[0:10].aggregate(Avg('time_taken'))['time_taken__avg'] for sc in scanner_classes]
    scanner_times = [int(sc) if sc != None else 0 for sc in scanner_times]
    scanner_timetable = [{
        'color': True if scanner_intervals[index] < scanner_times[index] else False, 
        'label': scanner_labels[index], 
        'time': timedelta(seconds=scanner_times[index]), 
        'interval': timedelta(seconds=scanner_intervals[index])} 
        for index, s in enumerate(scanner_classes)]
    
    users_count = 0
    for g in groups:
        try:
            users_in_group = GroupObservation.objects.filter(group=g.gid, statistics='total_users').latest("date").value
        except GroupObservation.DoesNotExist:
            users_in_group = 0
        users_count += users_in_group
        
    velocity_per_second = 200
    needed_per_second =  users_count / float(settings.GROUPS_SCAN_INTERVAL)
    credentials_needed = int(needed_per_second / velocity_per_second) + 1
   
    valid_credentials_count = len(get_credentials())
    return render_to_response ('groups.html', {'credentials_ok': valid_credentials_count >= credentials_needed, 
            'rec_credentials_count': credentials_needed, 'total_users': users_count, 'groups': groups, 
            'credentials_count': valid_credentials_count, 'timetable': scanner_timetable, 'total_posts': Post.objects.all().count()}, context_instance=RequestContext(request))
 