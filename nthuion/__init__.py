from pyramid.config import Configurator
import pyramid.renderers


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('.models')
    config.include('.routes')
    config.add_renderer(None, pyramid.renderers.JSON())
    config.scan()
    return config.make_wsgi_app()
