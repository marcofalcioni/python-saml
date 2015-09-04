from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    session_factory = SignedCookieSessionFactory(settings.get('session_secret'))
    authn_policy = AuthTktAuthenticationPolicy(settings.get('auth_secret'), hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings)

    config.set_session_factory(session_factory)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include('pyramid_chameleon')
    config.add_route('home', '/')
    config.add_route('attrs', '/attrs')
    config.add_route('metadata', '/metadata')
    config.scan()
    return config.make_wsgi_app()


