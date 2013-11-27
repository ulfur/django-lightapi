#encoding: utf-8

import json

from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View

from ... import get_version

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
		p = self.params.get( name, None )
		if p:
			try:
				return json.loads( p )
			except ValueError:
				return p
		return None
		
	def get_values( self ):
		values = self.get_param( 'values', None )
 		return json.loads( values ) if values else None

	def response( self, status, data ):
		res = HttpResponse( json.dumps( data ), content_type='application/json' )
		res.status_code = status
		return res

	def NotFound( self, data ):
		return self.response( 404, data )

	def ERROR( self, data ):
		return self.response( 400, data )
		
	def OK( self, data ):
		return self.response( 200, data )

class ServiceView( APIView ):

	def get_services( cls ):
		r = {}
		for k, v in cls._service_defs.items():
			r[k] = {
				'name':v['name'],
				'methods':v['methods'],
				'url':reverse( v['url-name'] )
			}
		return r

	def get( self, request, *args, **kwargs ):
		return self.OK( {'version':get_version(), 'services':self.get_services()} )