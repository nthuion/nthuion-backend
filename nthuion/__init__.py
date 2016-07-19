import sys

assert sys.version_info >= (3,)  # noqa


from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid import renderers

from .request import Request
from .auth.policies import TokenAuthenticationPolicy


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(
        request_factory=Request,
        authentication_policy=TokenAuthenticationPolicy(),
        authorization_policy=ACLAuthorizationPolicy(),
        settings=settings
    )
    config.include('.models')
    config.include('.routes')
    config.add_renderer(None, renderers.JSON())
    config.scan()
    return config.make_wsgi_app()
