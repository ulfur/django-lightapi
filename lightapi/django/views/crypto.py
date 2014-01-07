#encoding: utf-8

import json, base64

from django.conf import settings

from .base import APIView, ServiceView

from ...crypto.RSA import Lock, Key
from ...crypto.mixins import CryptoMixin

class CryptoAPIView( APIView, CryptoMixin ):

    def init_params( self, params ):
        print params
        data = self.decrypt( params, settings.LIGHTAPI_PRIVATEKEY )
        assert data is not None, 'Invalid encryption'
        
        self.client_key = data.pop( 'client_key', None )
        return super(CryptoAPIView, self).init_params( data )

    def prepare_data( self, data ):
        if hasattr(self, 'client_key') and self.client_key:
            data = self.encrypt( data, self.client_key )
            datastr = json.dumps( data ) 
        return super(CryptoAPIView, self).prepare_data(data)
        
