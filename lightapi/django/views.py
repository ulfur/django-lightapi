
import sys, json, inspect

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.conf import settings

from .. import get_version
from ..auth import ApiAuth

class APIView( View ):
	
	@classmethod
	def get_name( cls ):
		return getattr(cls, 'name', cls.__name__)
	
	@classmethod
	def get_methods( cls ):
		return getattr(cls, 'methods', ('get',))

	def dispatch( self, request, *args, **kwargs ):
		self.params = getattr( request, request.method )
		if hasattr( self, 'required_params' ):
			check, param = self.check_params( self.required_params )
			if not check:
				return HttpResponseBadRequest('Parameter "%s" is required.'%param)
			
		return super(APIView, self).dispatch(request, *args, **kwargs)
	
	def check_params( self, required ):
		for p in required:
			if p not in self.params.keys():
				return False, p
		return True, None
		
	def get_param( self, name ):
		return self.params.get( name, None )
		
	def get_values( self ):
		values = self.get_param( 'values', None )
 		return json.loads( values ) if values else None

	def response( self, status, data ):
		res = HttpResponse( json.dumps( data ), content_type='application/json' )
		res.status_code = status
		return res

	def OK( self, data ):
		return self.response( 200, data )

class APIProtectedView( APIView ):
	
	def dispatch( self, request, *args, **kwargs ):
		api_auth = ApiAuth( self.get_secret() )
		if not api_auth.is_valid( self.params.get('token') ):
			raise PermissionDenied( 'Your key didn\'t fit' )
		return super(APIProtectedView, self).dispatch(request, *args, **kwargs)
				
	def get_secret( self ):
		return self.secret

class ServiceView( APIView ):

	def get_services( cls ):
		r = {}
		for k, v in cls._service_defs.items():
			r[k] = v
			r[k]['url'] = reverse( r[k].pop('url-name') )
		return r

	def get( self, request, *args, **kwargs ):
		return self.OK( {'version':get_version(), 'services':self.get_services()} )




