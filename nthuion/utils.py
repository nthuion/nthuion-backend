from contextlib import contextmanager
from pyramid.httpexceptions import HTTPBadRequest


@contextmanager
def keyerror_is_bad_request():
    try:
        yield
    except KeyError as exc:
        raise HTTPBadRequest('missing required key {}'.format(exc))
