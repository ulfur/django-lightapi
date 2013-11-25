import json
from ..client import Client
from .RSA import Lock, Key

class EncryptedClient( Client ):
	
	def __init__( self, host, public_key=None, private_key=None, service_url='/services' ):
		self._public  = Lock( public_key )  if public_key  else None
		self._private = Lock( private_key ) if private_key else None
		super(EncryptedClient, self).__init__(host, service_url)
		
	def load_data( self, datastr ):
		
		if self._private:
			data = json.loads( datastr )
			datastr = self._private.decrypt( data['msg'], data['key'] )
		
		return super(EncryptedClient, self).load_data( datastr )
		
	def prepare_data( self, data ):
		
		if self._public:
			datastr = json.dumps( data )
			msg, key = self._public.encrypt( datastr )
			data = {
				'msg': msg,
				'key': key
			}
		
		return super(EncryptedClient, self).prepare_data( data )
