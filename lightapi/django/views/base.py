#encoding: utf-8

import ast, json, traceback

from django.core.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.generic import View

from ... import get_version

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
        self.init_params( request )
        check, param = self.check_params( )
        
        if not check:
            return HttpResponseBadRequest( 'Parameter "%s" is required.'%param )
            
        try:
            return super(APIView, self).dispatch(request, *args, **kwargs)
        except:
            return self.ERROR( )

    def init_params( self, request, params=None ):

        params = params if params else getattr( request, request.method, {} )

        self.params = dict( )
        for k, v in params.items():
            try:
                self.params[k] = ast.literal_eval( v )
            except:
                self.params[k] = v
        return self.params

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

    def get_param( self, name ):
        '''Returns the parameter named "name" or None if no such parameter exists
        '''
        return self.params.get( name, None )

    def prepare_data( self, data ):
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
        
    def NOK( self, status=400, data={ } ):
        '''The request could not be successfully completed for some reason'''
        return self.response( status, data )

    def UNAUTHORIZED( self, data={ } ):
        return self.NOK( status=401, data=data )

    def FORBIDDEN( self, data={ } ):
        return self.NOK( status=403, data=data )
        
    def NOTFOUND( self, data={ } ):
        '''The requested service or resource was not found'''
        return self.NOK( status=404, data=data )

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

