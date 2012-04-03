from group_spy.utils.misc import get_vk_crawler
from datetime import datetime, timedelta

# change groups here
groups = [10537686, 13611752, 15721446, 28729824, 33515]
crawler = get_vk_crawler()
for g in groups:
    f = open(str(g) + ".csv", "w")
    # change TIMEDELTA(Days=90)
    posts = [p for p in crawler.get_posts_from_group("-" + str(g), time.mktime((datetime.now() - timedelta(days=90)).timetuple()))]
    cl = crawler.get_comments_and_likes_for_posts(posts, "-" + str(g))
    users = {}
    for k, p in cl.iteritems():
        comments = p['comments']
        likes = p['likes']
        for c in comments:
            if not c['uid'] in users:
                users[c['uid']]= 0
            users[c['uid']] += 1
        for l in likes:
            if not l in users:
                users[l] = 0
            users[l] += 1
    users_list = users.items()
    users_list.sort(key=lambda tuple: tuple[1], reverse=True)
    # change count of users here
    users_list = users_list[0:50]
    user_ids = [u[0] for u in users_list]
    profiles = [p for p in crawler.get_profiles(user_ids)]
    final_list = [(u[0][0], u[1]['first_name'].decode('utf-8').encode('cp1251'), u[1]['last_name'].decode('utf-8').encode('cp1251'), u[0][1]) for u in zip(users_list, profiles)]
    for v in final_list:
        f.write(str(v[0]) + ";" + str(v[1]) + ";" + str(v[2]) + ";" + str(v[3]) + ";\n")
    f.close()
exit()