#encoding: utf-8

import json, base64

from django.conf import settings

from .base import APIView, ServiceView

from ...crypto.RSA import Lock, Key

class CryptoAPIView( APIView ):

    def init_params( self, request, params=None ):
        params = params if params else getattr( request, request.method, {} )

        lock = Lock( settings.API_PRIVATEKEY )

        #Get the b64 encoded and crypted key/message pair
        msg = params.get( 'msg', None )
        key = params.get( 'key', None )
        
        #b64decode the key/message pair
        msg = base64.b64decode(msg)
        key = base64.b64decode(key)

        #Decrypt the message
        data = lock.decrypt( msg, key )
        data = json.loads( data )
        return super(CryptoAPIView, self).init_params( request, params=data )
