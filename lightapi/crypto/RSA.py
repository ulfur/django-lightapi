import os
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import Crypto.Util.number

KEYSIZE = 16

class Key( object ):
	
	def __init__( self, key=None ):
		if key:
			self.importkey( key )
		else:
			self.create_key( )
	
	def create_key( self ):
		random = Random.new().read
		self._key = RSA.generate( 1024, random )
	
	def importkey( self, key ):
		self._key = RSA.importKey( key )
		
	@property
	def public( self ):
		return self._key.publickey().exportKey()
		
	@property
	def private( self ):
		if self._key.has_private():
			return self._key.exportKey()
		return None
		
class Lock( object ):
	
	def __init__( self, key, size=KEYSIZE ):
		self._key = RSA.importKey( key )
		self._key_size = size
	
	@property
	def _padding( self ):
		plaintext_length = (Crypto.Util.number.size(self._key.n) - 2) / 8
		padding = '\xff' + os.urandom( self._key_size )
		padding += '\0' * ( plaintext_length - len(padding) - self._key_size )
		return padding
	
	def encrypt( self, inp ):
		# Generate secret key
		secret_key = os.urandom( self._key_size )
	
		# Encrypt the secret key with RSA
		encrypted_key = self._key.encrypt( self._padding + secret_key, None )[0]

		aes = AES.new( secret_key, AES.MODE_CBC, '\x00' * self._key_size )

		inp += (16-len(inp)%16)*' '
		return aes.encrypt( inp ), encrypted_key
	
	def decrypt( self, inp, encrypted_key ):

		secret_key = self._key.decrypt( encrypted_key )

		secret_key = secret_key[len(self._padding):]

		aes = AES.new( secret_key, AES.MODE_CBC, '\x00'*16 )
	
		return aes.decrypt( inp ).strip()