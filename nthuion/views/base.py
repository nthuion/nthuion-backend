from pyramid.httpexceptions import HTTPMethodNotAllowed


class View:

    def __init__(self, request):
        self.request = request

    def __call__(self):
        try:
            func = self._methods[self.request.method]
        except KeyError:
            raise HTTPMethodNotAllowed
        else:
            return func()
