#encoding: utf-8

import json, base64

from django.conf import settings

from .base import APIView, ServiceView

from ...crypto.RSA import Lock, Key
from ...crypto.mixins import CryptoMixin

class CryptoAPIView( APIView, CryptoMixin ):

    def init_params( self, request, params=None ):
        params = params if params else getattr( request, request.method, {} )
        data = self.decrypt( params, settings.API_PRIVATEKEY )
        self.client_key = data.pop( 'client_key', None )
        return super(CryptoAPIView, self).init_params( request, params=data )

    def prepare_data( self, data ):
        if self.client_key:
            data = self.encrypt( data, self.client_key )
            datastr = json.dumps( data ) 
        return super(CryptoAPIView, self).prepare_data(data)
        
