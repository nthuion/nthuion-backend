from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError


@view_config(route_name='home')
def my_view(request):
    return {'hello': 'hello', 'world': 'world'}
