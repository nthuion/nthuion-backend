from pyramid.view import view_config
from .base import View


@view_config(route_name='echo')
class EchoView(View):

    def get(self):
        return self.request.params.dict_of_lists()

    def post(self):
        return self.json_body

    def put(self):
        return self.json_body
