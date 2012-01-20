import hashlib
import urllib2
import json
from group_spy.logger.error import LogError
import time

class VKRequest (object):
	
	_viewer_id = ''
	_sid = ''
	_secret = ''
	_service_params = {'format' : 'JSON', 'v': '3.0'}
	
	def __init__(self, credentials):
		self._viewer_id = credentials['viewer_id']
		self._sid = credentials['sid']
		self._secret = credentials['secret']
		self._service_params['api_id'] = credentials['api_id']
	
	def _create_params (self, params):
		res = {}
		for p in self._service_params:
			res[p] = self._service_params[p]
		for p in params:
			res[p] = params[p]
		return res
	
	def _vk_make_signature (self, params):
		sig_params = self._create_params (params)		
		sig_list = []
		for p in sig_params:
			sig_list.append ({'key' : p, 'value': sig_params[p]})
		sig_list = sorted(sig_list)
		hashee = self._viewer_id
		for l in sig_list:
			hashee += l['key'] + "=" + str (l['value'])
		hashee += self._secret
		md5hash = hashlib.md5 ()
		md5hash.update (hashee)
		sig = md5hash.hexdigest ()
		return sig
	
	def vk_create_url (self, params):
		url = "http://api.vkontakte.ru/api.php?sid=" + self._sid + "&sig=" + self._vk_make_signature(params)
		params = self._create_params (params)
		for p in params:
			url += "&" + p + "=" + str (params[p])
		return url
	
	def blocking_request (self, params, retries=10):
		url = self.vk_create_url(params)
		while True:
			try:
				f = urllib2.urlopen(url, timeout=2)
				response = f.read ()
				parsed = json.loads (response)
				if (not "response" in parsed) and (not "error" in parsed):
					raise NetworkError ()	
				if "response" in parsed:
					return parsed['response']
				else:
					raise VKAPIError (parsed['error'])
			except (Exception, NetworkError, VKAPIError) as err:
				if retries > 0:
					retries -= 1
					time.sleep (0.25)
					continue
				else:
					raise LogError (err)
		

class NetworkError(BaseException):
	pass	

class VKAPIError(BaseException):
	
	def __init__ (self, err):
		self.error_dict = err
		
	def to_s (self):
		return str(self.error_dict)
	