from functools import wraps
from pyramid.httpexceptions import (
    HTTPMethodNotAllowed,
    HTTPForbidden,
    HTTPUnauthorized
)


def not_allowed(self):
    raise HTTPMethodNotAllowed


class View:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    get = post = put = delete = not_allowed

    def options(self):
        # allow the js client to be on a different origin
        self.request.response.headers['Access-Control-Allow-Origin'] = '*'
        return {
            'permissions': self.get_permissions()
        }

    def get_permissions(self):
        # XXX: test this
        try:
            acls = self.context.__acl__
        except AttributeError:
            return []
        else:
            if callable(acls):
                acls = acls()
            return [
                perm for perm
                in set(acl[2] for acl in acls)
                if self.request.has_permission(perm)
            ]

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
            raise HTTPForbidden('no permission for {}'.format(perm))

    def add_view_count(self, dest=None):
        if dest is None:
            dest = self.context
            assert dest is not None
        if self.user is None:
            self.request.ts.article_viewed_by_ip(
                self.context,
                self.request.client_addr)
        else:
            self.request.ts.article_viewed_by_user(
                self.context,
                self.user)


class require_permission:

    def __init__(self, permission):
        self.permission = permission

    def __call__(reqp, function):
        permission = reqp.permission

        @wraps(function)
        def wrapper(self, *args, **kwargs):
            if not self.request.has_permission(permission):
                if self.user is None:
                    raise HTTPUnauthorized('authentication required')
                else:
                    raise HTTPForbidden(
                        'no permission for {}'.format(permission))
            return function(self, *args, **kwargs)

        wrapper.requires_permission = permission
        return wrapper
