import inspect

from django.conf.urls import patterns, url

from .views import APIView, ServiceView, EncryptedServiceView

def api_urls( module, ns='' ):
	urlpatterns = patterns('',)
	service_defs = { }
	for name, ob in inspect.getmembers(module):
		if inspect.isclass(ob) and ob.__module__ == module.__name__ and issubclass(ob,APIView):
			url_name = 'lightapi-%s'%ob.get_name()
			u = url( r'^%s$'%ob.get_name().lower(), ob.as_view(), name=url_name )
			urlpatterns.append( u )

			service_defs[ob.get_name()] = {
				'methods': ob.get_methods(),
				'name': ob.get_name(),
				'url-name': url_name
			}

	service_defs['services'] = {
		'methods': ('get',),
		'name': 'services',
		'url-name': 'lightapi-services'
	}
	
	class S( ServiceView ):
		_service_defs = service_defs
	urlpatterns.append( url(r'^services$', S.as_view(), name='lightapi-services') )	
	
	class SE( EncryptedServiceView ):
		_service_defs = service_defs
	urlpatterns.append( url(r'^enc/services$', S.as_view(), name='lightapi-services') )	
		
	return urlpatterns
