import hashlib
import urllib2
import json
import time
from datetime import datetime, timedelta

def is_user_banned(profile):
	return profile['photo'] == 'http://vk.com/images/deactivated_c.gif'

def augment_profiles_with_extended_geo_info(crawler, profiles):
	countries = {str(country['cid']): country['name'] for country in crawler.get_countries([c for c in {p['country'] for p in profiles if 'country' in p}])}
	cities = {city['cid']: city['name'] for city in crawler.get_cities([c for c in {p['city'] for p in profiles if 'city' in p}])}
	for p in profiles:
		if 'city' in p and p['city'] in cities:
			p['city_name'] = cities[p['city']]
		if 'country' in p and p['country'] in countries:
			p['country_name'] = countries[p['country']]
	return profiles

def augment_profiles_with_extended_age_info(profiles):
	now_year = datetime.now().year
	for p in profiles:
		if 'bdate' in p:
			pieces = p['bdate'].split(".")
			for piece in pieces:
				if len(piece) == 4:
					p['age'] = now_year - int(piece)
	return profiles

class VKCredentialsCollection(object):
	
	_collection = {}
	
	_file_path = None
	
	def __init__(self, file_path):
		self._file_path = file_path
		try:
			credentials_handle = open (file_path, "r")
			credentials = json.load (credentials_handle)
			credentials_handle.close()
			if not isinstance(credentials, list):
				raise Exception()
		except:
			return
		required_fields = ['api_id', 'viewer_id', 'sid', 'secret']
		raw_collection = [c for c in credentials if isinstance(c, dict) and len([r for r in required_fields if not r in c]) == 0]
		raw_set = {c['viewer_id'] + ":" + c['api_id']: c for c in raw_collection}
		self._collection = {VKCredentials(r['api_id'], r['viewer_id'], r['secret'], r['sid'], self) for r in raw_set.values()}
		self.test_all_credentials()
	
	def add_new_tested_credentials(self, credentials):
		try:
			same_viewer = (c for c in self._collection if c._viewer_id == credentials._viewer_id and c._api_id == credentials._api_id).next()
			self._collection.remove(same_viewer)
		except StopIteration:
			pass
		finally:
			self._collection.add(credentials)
			
	def remove_credentials_by_viewer(self, viewer_id, api_id):
		try:
			credentials = (c for c in self._collection if c._viewer_id == viewer_id and c._api_id == api_id).next()
			self._collection.remove(credentials)
		except StopIteration:
			pass
						
	def dump_to_disk(self):
		f = open(self._file_path, "w")
		all_credentials = self.get_all_credentials()
		json.dump([c.as_dictionary() for c in all_credentials], f)
		f.close()
	
	def get_credentials(self, exclude_creds=None):
		if exclude_creds:
			return [c for c in self._collection if c.is_valid() and not c in exclude_creds]
		else:
			return [c for c in self._collection if c.is_valid()]
	
	def get_all_credentials(self):
		return list(self._collection)
	
	def test_all_credentials(self):
		for c in list(self._collection):
			c.test()
		
	def credentials_gone_bad(self, credentials):
		print "VKCredentialsCollection -- invalid credentials found: " + str(credentials)
	
class VKCredentials (object):
	
	def __init__(self, api_id, viewer_id, secret, sid, parent_collection=None):
		self._viewer_id = viewer_id
		self._sid = sid
		self._secret = secret
		self._api_id = api_id
		self._service_params = {'format' : 'JSON', 'v': '3.0', 'api_id': api_id}
		self._valid = True
		self._parent_collection = parent_collection
		self._last_calls = []
	
	def as_dictionary(self):
		return {'api_id': self._service_params['api_id'], 'viewer_id': self._viewer_id, 'secret': self._secret, 'sid': self._sid, 'valid': self.is_valid()}
	
	def is_valid(self):
		return self._valid
	
	def test(self):
		try:
			self.blocking_request({'method': 'getProfiles', 'fields': 'sex,photo,bdate,education,city,country', 'uids': '1'})
		except:
			self._valid = False
	
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
		md5hash = hashlib.md5()
		md5hash.update (hashee)
		sig = md5hash.hexdigest()
		return sig
	
	def vk_create_url (self, params):
		url = "http://api.vkontakte.ru/api.php?sid=" + self._sid + "&sig=" + self._vk_make_signature(params)
		params = self._create_params (params)
		for p in params:
			url += "&" + p + "=" + str (params[p])
		return url
	
	def blocking_request (self, params, retries=10):
		url = self.vk_create_url(params)
		now = datetime.now()
		self._last_calls = [t for t in self._last_calls if now - t < timedelta(seconds=1)]
		if len(self._last_calls) >= 3:
			time.sleep(1 - (now - self._last_calls[1]).total_seconds())
		self._last_calls.append(datetime.now())
		while True:
			try:
				try:
					f = urllib2.urlopen(url, timeout=2)
				except (urllib2.URLError, urllib2.HTTPError) as err:
					#print "network error"
					raise NetworkError()
				response = f.read()
				parsed = json.loads(response)
				if (not "response" in parsed) and (not "error" in parsed):
					#print "malformed vk response"
					raise NetworkError()	
				if "response" in parsed:
					return parsed['response']
				else:
					error = parsed['error']
					#print error
					if not 'error_code' in error:
						#print "malformed vk response"
						raise NetworkError()
					error_code = error['error_code']
					if error_code == 4 or error_code == 5:
						raise InvalidCredentialsError()
					elif error_code == 6:
						raise TooManyRequestsError()
					else:
						print error['error_msg']
						raise VKAPIError(error)
			except NetworkError as err:
				retries -= 1
				if retries >= 0:
					time.sleep(0.1)
					continue
				else:
					raise err
			except InvalidCredentialsError as err:
				if self._parent_collection:
					self._parent_collection.credentials_gone_bad(self)
				self._valid = False
				raise err
			except TooManyRequestsError as err:
				#print "too many requests per second"
				time.sleep(0.3)
				continue
		
class NetworkError(Exception):
	pass	

class InvalidCredentialsError(Exception):
	pass

class TooManyRequestsError(Exception):
	pass

class VKAPIError(Exception):
	
	def __init__ (self, err):
		self.error_dict = err
		
	def to_s (self):
		return str(self.error_dict)
	