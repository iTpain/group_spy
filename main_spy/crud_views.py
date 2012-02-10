from group_spy.main_spy.views_utils import json_response, request_vk_credentials
from group_spy.main_spy.models import Group

@json_response
@request_vk_credentials
def add_group(request, gid, crawler):
    try:
        obj = Group.objects.filter(gid=gid)
        if len(obj) > 0:
            return {'errors': ['group already added']}
        for g in crawler.get_groups([gid]):
            group_name = g['name']
        new_group = Group(gid=gid, alias=group_name)
        new_group.save()
        return {'gid': gid, 'alias': group_name}
    except:
        return {'errors': ['Failed to save group']}
    
@json_response
def delete_group(request, gid):
    try:
        Group.objects.filter(gid=gid).delete()
        return {}
    except:
        return {'errors': ['Failed to delete group']}
    
@json_response
def update_group_info(request, group_id):
    group = Group.objects.get(gid=group_id)
    group.agency = request.POST['agency']
    group.brand = request.POST['brand']
    group.save()
    return {}
