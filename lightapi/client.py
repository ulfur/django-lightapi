#encoding: utf-8

import httplib, urllib, json, warnings, base64

from . import get_version

ERRORS = {
    400: 'Bad request.',
    403: 'Forbidden.',
    404: 'Service not found.',
    500: 'Server side error.',
}

class APIException( Exception ):
    pass

def assert_status( status, response='' ):
    if status != 200:
        error_msg = ERRORS.get( status, 'Undefined error (%i).'%status )
        raise APIException( 'ERROR (%i): %s\nResponse: %s'%(status,error_msg,response) )

class Client( object ):

    def __init__( self, host, service_url='/services' ):
        self._host = host

        status, response = self.request( service_url, method='GET' )
        assert_status( status, response )

        if response['version'] > get_version( ):
            warnings.warn('The server is running a more recent version than your client.\nErrors may ensue.', DeprecationWarning)
        self._services = response['services']

    def load_data( self, datastr ):
        return json.loads( datastr )

    def prepare_data( self, data ):
        return data

    def request( self, path, method='POST', service='', **data ):
        http = httplib.HTTPConnection( self._host )

        data = self.prepare_data( data )

        data = urllib.urlencode( data )

        if method=='POST':
            head = { 'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain' }
            http.request( method, path, data, head )
        else:
            url = '%s?%s'%(path,data) if data else path
            http.request( method, url )

        response = http.getresponse( )
        res = response.read( )

        assert_status( response.status, res )

        return response.status, self.load_data( res )

    def __getattr__( self, name ):
        try:
            method, name = name.split('_', 1)
            if name in self._services.keys() and method in self._services[name]['methods']:
                return lambda **data: self.request( self._services[name]['url'], method=method.upper(), service=name, **data )
        except:
            pass
        raise TypeError( 'API has no service called: %s'%name )
        
