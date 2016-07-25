import functools
from pyramid.httpexceptions import HTTPBadRequest
from voluptuous import *
# from voluptuous.humanize import humanize_error


class body_schema(Schema):

    def __call__(schema, meth):
        @functools.wraps(meth)
        def wrapper(view):
            try:
                data = super(
                    body_schema, schema).__call__(view.request.json_body)
            except MultipleInvalid as e:
                raise HTTPBadRequest(str(e))
            return meth(view, data)
        return wrapper
