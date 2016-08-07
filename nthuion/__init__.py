import sys

assert sys.version_info >= (3,)  # noqa


from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid import renderers

from .request import Request
from .authentication_policy import TokenAuthenticationPolicy


def get_config(global_config, **settings):
    config = Configurator(
        request_factory=Request,
        authentication_policy=TokenAuthenticationPolicy(),
        authorization_policy=ACLAuthorizationPolicy(),
        settings=settings
    )
    config.include('.models')
    config.include('.routes')
    config.include('.traffic')
    config.add_renderer(None, renderers.JSON())
    return config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    return get_config(global_config, **settings).make_wsgi_app()
