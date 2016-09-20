import sys

assert sys.version_info >= (3,)  # noqa


import os
import random
import string
from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid import renderers
from itsdangerous import URLSafeTimedSerializer

from .request import Request
from .authentication_policy import TokenAuthenticationPolicy


def random_string(length, candidates=string.ascii_letters + string.digits):
    rnd = random.SystemRandom()
    return ''.join(rnd.choice(candidates) for i in range(length))


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
    signer = URLSafeTimedSerializer(
        os.environ.get('NTHUION_SECRET') or random_string(128)
    )
    config.add_request_method(
        lambda r: signer,
        'signer',
        reify=True
    )
    return config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    return get_config(global_config, **settings).make_wsgi_app()
