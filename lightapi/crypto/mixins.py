#encoding: utf-8

import json, base64
from ..client import Client
from .RSA import Lock, Key


class CryptoMixin( object ):
    
    def encrypt( self, data, enckey ):

        datastr = json.dumps( data ) 
        l = Lock( enckey )
        msg, key = l.encrypt( datastr )
        data = {
            'msg': base64.b64encode( msg ),
            'key': base64.b64encode( key ),
        }
        return data
    
    def decrypt( self, data, enckey ):
        #Get the b64 encoded and crypted key/message pair
        msg = data.get( 'msg', None )
        key = data.get( 'key', None )
        
        if msg and key:
        
            #b64decode the key/message pair
            msg = base64.b64decode( msg )
            key = base64.b64decode( key )

            l = Lock( enckey )
            datastr = l.decrypt( msg, key )
            data = json.loads( datastr )

        return data