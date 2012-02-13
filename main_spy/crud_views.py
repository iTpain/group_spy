from group_spy.main_spy.views_utils import json_response, request_vk_credentials
from group_spy.main_spy.models import Group, TextCategory, PostTextCategoryAssignment, Post

@json_response
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
    
@json_response
def delete_group(request, group_id):
    try:
        Group.objects.filter(gid=group_id).delete()
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

@json_response
def get_posts(request, group_id, start, count):
    start = int(start)
    count = int(count)
    posts = Post.objects.filter(group=group_id).order_by('-id')[start : start + count]
    posts = [{'id': p.id, 'text': p.text, 'categories': [c.category.id for c in p.posttextcategoryassignment_set.all()]} for p in posts]
    return posts

@json_response
def get_text_categories(request, group_id):
    group = Group.objects.get(gid=group_id)
    return [{'id': c.id, 'alias': c.alias} for c in group.text_categories.all()]

@json_response
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

@json_response    
def update_text_category(request, id):
    alias = request.POST['alias']
    try:
        category = TextCategory.objects.get(pk=id)
    except:
        return {'errors': ['Failed to fetch category']}
    category.alias = alias
    category.save()
    return {}
    
@json_response
def remove_text_category(request, id):
    TextCategory.objects.get(pk=id).delete()
    return {}

@json_response
def associate_text_category_with_post(request, post_id, category_id):
    association = PostTextCategoryAssignment(post_id=int(post_id), category_id=int(category_id), assigned_by_human=True)
    association.save()
    return {}

@json_response
def deassociate_text_category_with_post(request, post_id, category_id):
    association = PostTextCategoryAssignment.objects.filter(post=int(post_id), category=int(category_id))
    association.delete()
    return {}
