#encoding: utf-8

import inspect

from django.conf.urls import patterns, url

from .views import APIView, CryptoAPIView, ServiceView

def api_urls( module, ns='' ):
    urlpatterns = patterns('',)
    service_defs = { }

    for name, ob in inspect.getmembers( module ):
        if inspect.isclass( ob ) and ob.__module__ == module.__name__ and issubclass( ob,APIView ):
            url_name = 'lightapi-%s'%ob.get_name( )
            u = url( r'^%s$'%ob.get_name( ).lower( ), ob.as_view( ), name=url_name )
            urlpatterns.append( u )

            service_defs[ ob.get_name() ] = {
                'methods': ob.get_methods(),
                'name': ob.get_name(),
                'url-name': url_name,
                'encrypted': issubclass(ob,CryptoAPIView)
            }

    service_defs['services'] = {
        'methods': ('get',),
        'name': 'services',
        'url-name': 'lightapi-services',
        'encrypted': False
    }

    class S( ServiceView ):
        services = service_defs
    urlpatterns.append( url(r'^services$', S.as_view(), name='lightapi-services') )

    return urlpatterns
