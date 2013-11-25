

class BaseCache( object ):
	
	def __init__( self, key, ):
		self._key = key
	
	@property
	def cache( self ):
		return self.get( self._key )
	
	@cache.setter
	def cache( self, value ):
		self.set( value )
		
	def set( self, value ):
		pass
	
	def get( self ):
		return value
		
	def stale( self ):
		pass
	