from pkg_resources import resource_filename
from pyramid.config import Configurator
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request
from repoze.zodbconn.finder import PersistentApplicationFinder
import deform

from nhssl.resources import appmaker
from nhssl.security import groupfinder
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


def translator(term):
    return get_localizer(get_current_request()).translate(term)


class NonPersistentApplicationFinder(PersistentApplicationFinder):

    def __call__(self, environ):
        app = self.appmaker({})
        return app


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    zodb_uri = settings.get('zodb_uri')
    if zodb_uri is None:
        finder_class = NonPersistentApplicationFinder
    else:
        finder_class = PersistentApplicationFinder
    finder = finder_class(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)
    deform_template_dir = resource_filename('deform', 'templates/')
    deform.Form.set_zpt_renderer(deform_template_dir, translator=translator)
    authentication_policy = AuthTktAuthenticationPolicy(secret='seekrit',
                                                        callback=groupfinder)
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(root_factory=get_root, settings=settings,
							authentication_policy = authentication_policy,
							authorization_policy = authorization_policy,)
    config.add_static_view('static', 'nhssl:static')
    config.add_static_view('static_deform', 'deform:static')
    config.add_translation_dirs('nhssl:locale', 'colander:locale', 'deform:locale')
    config.scan('nhssl')
    return config.make_wsgi_app()
