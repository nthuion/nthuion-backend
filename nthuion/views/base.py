from json import JSONDecodeError
from pyramid.httpexceptions import HTTPMethodNotAllowed, HTTPBadRequest


class View:

    def __init__(self, request):
        self.request = request

    @property
    def json_body(self):
        """
        wrapper of self.request.json_body
        raises HTTPBadRequest on invalid
        """
        try:
            return self.request.json_body
        except JSONDecodeError:
            raise HTTPBadRequest('invalid json')

    def get(self):
        raise HTTPMethodNotAllowed

    def post(self):
        raise HTTPMethodNotAllowed

    def put(self):
        raise HTTPMethodNotAllowed

    def delete(self):
        raise HTTPMethodNotAllowed

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
