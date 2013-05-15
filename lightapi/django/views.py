import json

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings

from .. import VERSION
from ..auth import ApiAuth


class APIProtectedView( View ):
	
	def dispatch( self, request, *args, **kwargs ):
		self.params = getattr( request, request.method )
		api_auth = ApiAuth( self.get_secret() )
		if not api_auth.is_valid( self.params.get('token') ):
			raise PermissionDenied( 'Your key didn\'t fit' )
		return super(APIProtectedView, self).dispatch(request, *args, **kwargs)
				
	def get_secret( self ):
		return self.secret
		
	def get_values( self ):
 		return json.loads( self.params.get( 'values' ) )

	def response( self, status, data ):
		res = HttpResponse( json.dumps( data ), content_type='application/json' )
		res.status_code = status
		return res

	def OK( self, data ):
		return self.response( 200, data )
		
		
class ServiceView( APIProtectedView ):

	def get( self, request, *args, **kwargs ):
		return self.OK( {'version':VERSION, 'services':self.get_services()} )
		
	def get_services( self ):
		return self.services
