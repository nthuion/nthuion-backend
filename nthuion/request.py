try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
from pyramid.httpexceptions import HTTPBadRequest
import pyramid.request
import pyramid.testing


class Mixin:

    @property
    def json_body(self):
        """
        get body as JSON
        raises HTTPBadRequest on invalid
        """
        try:
            return super().json_body
        except JSONDecodeError:
            raise HTTPBadRequest('invalid json')


class Request(Mixin, pyramid.request.Request):
    pass


class DummyRequest(Mixin, pyramid.testing.DummyRequest):
    pass
