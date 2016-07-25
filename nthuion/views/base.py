from functools import wraps
from pyramid.httpexceptions import HTTPMethodNotAllowed, HTTPUnauthorized


def not_allowed(self):
    raise HTTPMethodNotAllowed


class View:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    get = post = put = delete = not_allowed

    def options(self):
        # make life easier
        # facebook graph api sets this header too
        self.request.response.headers['Access-Control-Allow-Origin'] = '*'

    def __call__(self):
        method = self.request.method
        if method == 'GET':
            return self.get()
        elif method == 'POST':
            return self.post()
        elif method == 'PUT':
            return self.put()
        elif method == 'DELETE':
            return self.delete()
        elif method == 'OPTIONS':
            return self.options()
        else:
            raise HTTPMethodNotAllowed

    @property
    def db(self):
        return self.request.db

    @property
    def user(self):
        return self.request.authenticated_userid

    def check_permission(self, perm):
        has_perm = self.request.has_permission(perm)
        if not has_perm:
            raise HTTPUnauthorized('no permission for {}'.format(perm))


class require_permission:

    def __init__(self, permission):
        self.permission = permission

    def __call__(reqp, function):
        permission = reqp.permission

        @wraps(function)
        def wrapper(self, *args, **kwargs):
            if not self.request.has_permission(permission):
                raise HTTPUnauthorized(
                    'no permission for {}'.format(permission))
            return function(self, *args, **kwargs)
        return wrapper
