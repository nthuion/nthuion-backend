import functools
from pyramid.httpexceptions import HTTPBadRequest
from voluptuous import *


class qs_schema(Schema):

    def __call__(schema, meth):
        @functools.wraps(meth)
        def wrapper(view):
            try:
                data = super(
                    qs_schema, schema).__call__(view.request.params.mixed())
            except MultipleInvalid as e:
                raise HTTPBadRequest(str(e))
            return meth(view, data)
        wrapper.qs_schema = schema.schema
        return wrapper


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
        wrapper.schema = schema.schema
        return wrapper
