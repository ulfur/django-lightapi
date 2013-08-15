from datetime import datetime
from hashlib import sha256
	
class ApiAuth( object ):
	
	def __init__( self, secret ):
		self._secret = secret
		
	def generate_key( self ):
		t = datetime.utcnow().strftime( '%H:%M' )
		key = '%s%s'%(self._secret,t)
		return sha256( key ).hexdigest()
	
	def is_valid( self, key ):
		k = self.generate_key( )
		return key == self.generate_key( )