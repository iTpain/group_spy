#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from group_spy import settings
from group_spy.main_spy.models import Group, ScanStats, GroupObservation, Post, User, UserSocialAction
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from datetime import timedelta  

def crossdomainXML(request):
    response = HttpResponse()
    response.write('<cross-domain-policy><allow-access-from domain="*"/></cross-domain-policy>')
    return response

@login_required
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
        for index in xrange(len(scanner_classes))]
    
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

    return render_to_response ('groups.html', {'social_actions_stored': UserSocialAction.objects.count(),
            'rec_credentials_count': credentials_needed, 'total_users': users_count, 'groups': groups,  'username': request.user.username, 'accounts_stored': User.objects.count(),
            'timetable': scanner_timetable, 'total_posts': Post.objects.all().count()}, context_instance=RequestContext(request))

