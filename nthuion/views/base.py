from pyramid.httpexceptions import HTTPMethodNotAllowed, HTTPBadRequest


def not_allowed(self):
    raise HTTPMethodNotAllowed


class View:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    get = post = put = delete = not_allowed

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
        else:
            raise HTTPMethodNotAllowed

    @property
    def db(self):
        return self.request.db

    def check_permission(self, perm):
        has_perm = self.request.has_permission(perm)
        if not has_perm:
            raise HTTPBadRequest('no permission for {}'.format(perm))
