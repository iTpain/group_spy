#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management import setup_environ
import imp

imp.find_module("settings")

import settings
setup_environ(settings)

from babysitter.daemon import launch
from group_spy.main_spy.group_scan import GroupScanner
from group_spy.main_spy.post_scan import PostsScanner
from group_spy.main_spy.views import get_series_for_posts, get_social_activity_for_intraday_stratas, get_all_stats_series_for_posts, get_social_activity_for_intraweek_stratas
from group_spy.main_spy.models import Post, LatestPostObservation, PostObservation, GroupObservation, Group, PostAttachment
from datetime import datetime
from group_spy.textmine.vocabulary import Stemmer, StopWordsFilter, VocabularyTransform
from HTMLParser import HTMLParser

#stemmer = Stemmer("c:/projects/mystem.exe")
#stemmed = stemmer.stem_text(u'Бородатая Марина пошла в магазин и купила кроссовки nike. Ее поддержалм Моцарт и Сальери, которые знатно напились до красно-синего цвета лица.')
#words = StopWordsFilter("c:/users/projects/eclipse_projects/group_spy/group_spy/textmine/stop_words.in", stemmer).cleanse(stemmed)

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def prepare_corpus():
    parser = HTMLParser()
    posts = Post.objects.filter(group='13643401')[0:500]
    file = open("c:/users/projects/eclipse_projects/group_spy/group_spy/textmine/corpus.in", "w")
    for p in posts:
        text = strip_tags(p.text)
        text.replace('\n', ' ')
        file.write(text)
        file.write('\n\n')

prepare_corpus()
exit()    

parser = HTMLParser()
posts = Post.objects.filter(group='13643401')[0:500]
for p in posts:
    print strip_tags(p.text)
    print "****************"
documents = [p.text for p in posts]
v = VocabularyTransform.make("c:/projects/mystem.exe", "c:/users/projects/eclipse_projects/group_spy/group_spy/textmine/stop_words.in")
(v, c) = v.create_from_texts(documents)
for c1 in c:
    print c1

exit()

#past = datetime.now()
#http://localhost:8000/series/group13643401/social_dynamics_all//1296385474/1327921474/
#get_all_stats_series_for_posts(None, '13643401', '', '1296385474', '1327921474')
#http://localhost:8000/group21977113/intraday_stratify/1325585275/1328177275/
#get_social_activity_for_intraday_stratas(None, '21977113', '1325585275', '1328177275')
#print "oook"
#detmir - 31769636 adidas sport - 13643401
#print datetime.now() - past
#exit()

#http://localhost:8000/series/group21977113/social_dynamics/all/reposts/1326791430/1327557922/
#get_series_for_posts(None, '21977113', 'reposts', '', '1326791430', '1327557922')
#http://localhost:8000/group13643401/intraday_stratify/1325068941/1327660941/
#get_social_activity_for_intraday_stratas(None, '13643401', '1325068941', '1327660941')
#print datetime.now() - past
#exit()

#Post.objects.all().delete()
#GroupObservation.objects.all().delete()
#PostObservation.objects.all().delete()
#PostAttachment.objects.all().delete()
#LatestPostObservation.objects.all().delete()

launch([PostsScanner, GroupScanner], [settings.POSTS_SCAN_INTERVAL, settings.GROUPS_SCAN_INTERVAL])
#launch([GroupScanner], [settings.GROUPS_SCAN_INTERVAL])