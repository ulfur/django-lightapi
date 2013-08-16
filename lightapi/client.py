import httplib, urllib, json, warnings

from . import get_version
from .auth import ApiAuth

ERRORS = {
	403: 'The key doesn\'t fit.',
	404: 'Service not found.',
	500: 'Server side error.',
}

class APIException( Exception ):
	pass
	
def assert_status( status ):
	if status != 200:
		raise APIException( ERRORS.get( status, 'Undefined error (%i).'%status) )
	
class Client( object ):

	def __init__( self, host, secret, key=None, service_url='/services' ):
		self._key = key
		self._auth = ApiAuth( secret )
		self._host = host
		status, response = self.request( service_url, None, method='GET' )

		assert_status( status )

		if response['version'] > get_version():
			warnings.warn('The server is running a more recent version than your client.\nErrors may ensue.', DeprecationWarning)

		self._services = response['services']
		
	def generate_data( self, data ):
		package = {'values':json.dumps(data), 'token':self._auth.generate_key()}
		if self._key: package.update( {'key':self._key} )
		return urllib.urlencode( package )

	def load_data( self, datastr ):
		return json.loads( datastr )
		
	def request( self, path, data, method='POST' ):
		http = httplib.HTTPConnection( self._host )
		data = self.generate_data( data )
		
		if method=='POST':
			head = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain' }
			http.request( method, path, data, head )
		else:
			http.request( method, '%s?%s'%(path,data) )

		response = http.getresponse( )

		assert_status( response.status )		

		return response.status, self.load_data( response.read( ) )
				
	def __getattr__( self, name ):
		try:
			method, name = name.split('_')
			if name in self._services.keys() and method in self._services[name]['methods']:
				return lambda *data: self.request( self._services[name]['location'], data, method=method.upper() )
		except:
			pass
		raise TypeError( 'API has no service called: %s'%name )