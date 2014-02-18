#encoding: utf-8

import json, traceback
from datetime import date, datetime

from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.generic import View

from ... import get_version

from ...value_utils import parse_value

class APIView( View ):
    '''APIView is the base class for exposing services.
    Classes inheriting APIView need to implement at least one http request method (GET, POST, etc).
    The class name is used as the exposed service name unless the inheriting class defines a class attribute "name".
    If the services exposes methods other than GET it must define them using a class attribute "methods" as a tuple of available methods.
    '''
    
    @classmethod
    def get_name( cls ):
        '''Returns the name of the service. 
        Used for service discovery and announcement.
        '''
        return getattr(cls, 'name', cls.__name__)

    @classmethod
    def get_methods( cls ):
        '''Returns the available request methods (GET, POST, etc) of the service. 
        Used for service discovery and announcement.
        '''
        return getattr(cls, 'methods', ('get',))
    
    def dispatch( self, request, *args, **kwargs ):
        '''Returns HTTPResponse
        Service request entry point.
        '''
        if request.method.lower() not in self.get_methods():
            return self.METHODNOTALLOWED()
        
        try:    
            self.params = self.init_params( dict( getattr( request, request.method, {} ) ) )
        except AssertionError:
            return self.FORBIDDEN( )
            
        check, param = self.check_params( )
        if not check:
            return self.NOK( reason='Parameter "%s" is required.'%param )
        
        try:
            return super(APIView, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            return self.ERROR( )

    def init_params( self, params ):
        for k, v in params.items( ):
            if v:
                v = v[ 0 ] if isinstance( v, list ) and len( v ) > 0 else v
                v = parse_value( v )
            params[ k ] = v
        return params

    def process_params( self, params ):
        '''Returns processed parameters
        Classes inheriting this class may need to process the request parameters before
        passing them on to the main logic of the instance. E.g. removing encryption in
        the case of APICryptoView.
        '''
        return params

    def check_params( self, required=None ):
        '''Returns boolean
        Returns True if all the required parameters are present in the request and False if not.
        '''
        required = required if required else getattr( self, 'required_params', [] )
        for p in required:
            if p not in self.params.keys():
                return False, p
        return True, None

    def get_param( self, name, default=None ):
        '''Returns the parameter named "name" or None if no such parameter exists
        '''
        return self.params.get( name, default )

    def print_data( self, data, indent=0 ):
        print '\t'*indent, type(data)
        if isinstance( data, dict ):
            for k, v in data.items():
                self.print_data( v, indent=indent+1 )
        elif isinstance(data, list) or isinstance(data,tuple):
            for l in data:
                self.print_data( l, indent=indent+1 )
                        
    def prepare_data( self, data ):
        data = parse_value( data )
        
        try:
            from bson import json_util
            return json.dumps( data, default=json_util.default )
        except:
            pass
        return json.dumps( data )
        
    def response( self, status, data, success=False, headers={ } ):
        '''Return a response to the request
                status: The http status code for the response
                data: Any data expected in response to the request
                success: Did the request succeed or fail?
        '''
        data['success'] = success
        data = self.prepare_data( data )
        res = HttpResponse( data, content_type='application/json' )
        
        res.status_code = status
        return res

    # Canned responses. Using the response function is perfectly acceptable.
    # However, it can be argued that using the canned responses below instead
    # can improve the readability of the code using the framework.
    # Detailed explanations of each HTTP status code is provided by the W3C at:
    # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
    
    def OK( self, status=200, data={ } ):
        '''The request was successfully completed with in the expected manner'''
        return self.response( status, data, success=True )

    def CREATED( self, data={ } ):
        return self.OK( status=201, data=data )

    def ACCEPTED( self, data={ } ):
        return self.OK( status=202, data=data )
    
    def NOCONTENT( self ):
        return self.OK( status=204 )
        
    def NOK( self, status=400, reason='', data={ } ):
        '''The request could not be successfully completed for some reason'''
        data['reason'] = reason
        return self.response( status, data )

    def UNAUTHORIZED( self, data={ } ):
        return self.NOK( status=401, data=data )

    def FORBIDDEN( self, data={ } ):
        return self.NOK( status=403, reason='Forbidden', data=data )
        
    def NOTFOUND( self, reason='Not found', data={ } ):
        '''The requested service or resource was not found'''
        return self.NOK( status=404, reason=reason, data=data )
    
    def METHODNOTALLOWED( self ):
        return self.NOK( status=405, reason='Method not allowed', data={'available_methods':self.get_methods()})
        
    def ERROR( self, status=500, data={ } ):
        '''Catastrophic failure. The server ran into an unexpected exception'''
        data['trace'] = traceback.format_exc( )
        return self.response( status, data )

    def NOTIMPLEMENTED( self, data={ } ):
        return self.ERROR( status=501, data=data )
        
    def UNAVAILABLE( self, data={ } ):
        return self.ERROR( status=503, data=data )
        
class ServiceView( APIView ):
    '''ServiceView is a base view for announcing the services available.
    Available services are defined using the class attribute "services" as a dict.
    '''

    def get_services( cls ):
        '''Returns a dict of available services along with their details
        The only reason this is a seperate funcion and why it needs to copy
        the "services" dict is to be able to work with reversable urls.
        '''
        r = {}
        for k, v in cls.services.items():
            r[k] = {
                'name':v['name'],
                'methods':v['methods'],
                'url':reverse( v['url-name'] ),
                'encrypted': v['encrypted']
            }
        return r

    def get( self, request, *args, **kwargs ):
        return self.OK( data={'version':get_version(), 'services':self.get_services()} )

