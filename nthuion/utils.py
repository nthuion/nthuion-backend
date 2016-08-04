from contextlib import contextmanager
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound


@contextmanager
def keyerror_is_bad_request():
    try:
        yield
    except KeyError as exc:
        raise HTTPBadRequest('missing required key {}'.format(exc))


@contextmanager
def noresultfound_is_404():
    try:
        yield
    except NoResultFound:
        raise HTTPNotFound
