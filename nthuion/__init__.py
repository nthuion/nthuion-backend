import sys

assert sys.version_info >= (3,)  # noqa


from pyramid.config import Configurator
import pyramid.renderers
from .request import Request


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(request_factory=Request, settings=settings)
    config.include('.models')
    config.include('.routes')
    config.add_renderer(None, pyramid.renderers.JSON())
    config.scan()
    return config.make_wsgi_app()
