from flickr import settings as s
from urllib import request, parse
import simplejson as json
    
class Photo:
  API_URL = "https://api.flickr.com/services/rest/?%s"
  
  def api_auth(func):
    def add_auth(self, params):
      params.update(self.get_api_key())
      return func(self, params)
    return add_auth
    
  def api_method(method):
    def decorator(func):
      def wrapper(self, params):
        params.update({ 'method' : method, 'format' : 'json', 'nojsoncallback' : 1 })
        return func(self, params)
      return wrapper
    return decorator
  
  @api_auth
  @api_method('flickr.photos.search')
  def search(self, params):
    encoded = parse.urlencode(params)
    ret = request.urlopen(self.API_URL % encoded)
    return json.loads(ret.read())
    
  @api_auth
  @api_method('flickr.photos.getinfo')
  def get_info(self, params):
    encoded = parse.urlencode(params)
    ret = request.urlopen(self.API_URL % encoded)
    return json.loads(ret.read())
    
  def get_api_key(self):
    return { 'api_key' : s.API_KEY }
  