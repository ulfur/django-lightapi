
import json

from django.conf import settings

from .base import APIView

from ...crypto.RSA import Lock, Key

class APICryptoView( APIView ):
	
	def dispatch( self, request, *args, **kwargs ):
		self.params = getattr( request, request.method )

		lock = Lock( settings.API_PRIVATEKEY )
		msg = self.get_param( 'msg' )
		key = self.get_param( 'key' )
		
		data = lock.decrypt( msg, key )
		self.params = json.loads( data )
		
		if hasattr( self, 'required_params' ):
			check, param = self.check_params( self.required_params )
			if not check:
				return HttpResponseBadRequest('Parameter "%s" is required.'%param)
			
		return super(APIView, self).dispatch(request, *args, **kwargs)

class EncryptedServiceView( APICryptoView ):

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