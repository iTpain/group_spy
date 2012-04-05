from group_spy.main_spy.views_utils import request_vk_credentials, login_required_json_response
from group_spy.main_spy.models import Group, TextCategory, PostTextCategoryAssignment, Post
from group_spy import settings
from group_spy.utils.vk import VKCredentialsCollection, VKCredentials

@login_required_json_response
def get_groups(request):
    groups = list(Group.objects.all())
    return [{'gid': g.gid, 'brand': g.brand, 'agency': g.agency, 'alias': g.alias} for g in groups]

@login_required_json_response
@request_vk_credentials
def add_group(request, group_id, crawler):
    try:
        obj = Group.objects.filter(gid=group_id)
        if len(obj) > 0:
            return {'errors': ['group already added']}
        for g in crawler.get_groups([group_id]):
            group_name = g['name']
        new_group = Group(gid=group_id, alias=group_name)
        new_group.save()
        return {'gid': group_id, 'alias': group_name}
    except:
        return {'errors': ['Failed to save group']}

@login_required_json_response
def delete_group(request, group_id):
    try:
        Group.objects.filter(gid=group_id).delete()
        return {}
    except:
        return {'errors': ['Failed to delete group']}

@login_required_json_response
def update_group_info(request, group_id):
    group = Group.objects.get(gid=group_id)
    group.agency = request.POST['agency']
    group.brand = request.POST['brand']
    group.save()
    return {}

@login_required_json_response
def get_posts(request, group_id, start, count, only_by_group):
    start = int(start)
    count = int(count)
    objects = Post.objects.filter(group=group_id)
    if only_by_group == 'group':
        objects = objects.filter(author_is_group=True)
    posts = objects.order_by('-date')[start : start + count]
    posts = [{'author': p.author.snid if p.author != None else None, 'id': p.id, 'text': p.text, 'date': str(p.date), 'categories': [c.category.id for c in p.posttextcategoryassignment_set.all()]} for p in posts]
    return posts

@login_required_json_response
def get_text_categories(request, group_id):
    group = Group.objects.get(gid=group_id)
    return [{'id': c.id, 'alias': c.alias} for c in group.text_categories.all()]

@login_required_json_response
def add_text_category(request, group_id):
    alias = request.POST['alias']
    category = list(TextCategory.objects.filter(alias=alias))
    if len(category) == 0:
        category = TextCategory(alias=alias)
        category.save()        
    else:
        category = category[0]
    group = Group.objects.filter(gid=group_id)[0]
    for c in group.text_categories.all():
        if c.id == category.id:
            return {'errors': ['Already present']}
    group.text_categories.add(category)
    return {'id': category.id}

@login_required_json_response  
def update_text_category(request, category_id):
    alias = request.POST['alias']
    try:
        category = TextCategory.objects.get(pk=category_id)
    except:
        return {'errors': ['Failed to fetch category']}
    category.alias = alias
    category.save()
    return {}

@login_required_json_response
def remove_text_category(request, category_id):
    TextCategory.objects.get(pk=category_id).delete()
    return {}

@login_required_json_response
def associate_text_category_with_post(request, post_id, category_id):
    association = PostTextCategoryAssignment(post_id=int(post_id), category_id=int(category_id), assigned_by_human=True)
    association.save()
    return {}

@login_required_json_response
def deassociate_text_category_with_post(request, post_id, category_id):
    association = PostTextCategoryAssignment.objects.filter(post=int(post_id), category=int(category_id))
    association.delete()
    return {}

@login_required_json_response
def get_credentials(request):
    collection = VKCredentialsCollection(settings.VK_CREDENTIALS_FILE_PATH)
    all_credentials = [c.as_dictionary() for c in collection.get_all_credentials()]
    return all_credentials

@login_required_json_response
def add_credentials(request, api_id, viewer_id, sid, secret):
    credentials = VKCredentials(api_id, viewer_id, secret, sid)
    credentials.test()
    if not credentials.is_valid():
        return {'errors': ['Credentials seems to be broken']}
    collection = VKCredentialsCollection(settings.VK_CREDENTIALS_FILE_PATH)
    collection.add_new_tested_credentials(credentials)
    collection.dump_to_disk()
    return {}
    
@login_required_json_response
def delete_credentials(request, viewer_id, api_id):
    collection = VKCredentialsCollection(settings.VK_CREDENTIALS_FILE_PATH)
    collection.remove_credentials_by_viewer(viewer_id, api_id)
    collection.dump_to_disk()
    return {}
    