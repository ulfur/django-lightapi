#encoding: utf-8

import json, base64
from ..client import Client
from .RSA import Lock, Key
from .mixins import CryptoMixin

class EncryptedClient( Client, CryptoMixin ):

    def __init__( self, host, public_key, service_url='/services' ):
        self._public_key  = Key( public_key )
        self._private_key = Key()
        super(EncryptedClient, self).__init__(host, service_url)

    def load_data( self, datastr ):
        data = json.loads( datastr )
        return self.decrypt( data, self._private_key.private )
        
    def prepare_data( self, data ):
        data['client_key'] = self._private_key.public
        return self.encrypt( data, self._public_key.public )