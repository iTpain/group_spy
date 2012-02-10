from django.http import HttpResponse
from group_spy.utils.misc import get_vk_crawler
import json

# json response decorator
def json_response(func):
    def wrapper (*args, **kwargs):
        response = func (*args, **kwargs)
        if not ('errors' in response):
            response = {'response': response, 'errors': []}
        return HttpResponse (json.dumps (response), mimetype='application/json')
    return wrapper

# vk api credentials decorator
def request_vk_credentials(func):
    def wrapper (*args, **kwargs):
        crawler = get_vk_crawler ()
        if crawler == None:
            return {'errors': ['Unable to get vk api credentials']}
        else:
            kwargs['crawler'] = crawler;
        return func (*args, **kwargs)
    return wrapper  