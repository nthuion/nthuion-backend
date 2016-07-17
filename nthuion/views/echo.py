from pyramid.view import view_config


@view_config(route_name='echo', request_method='GET')
def echo_get(request):
    return request.params.dict_of_lists()


@view_config(route_name='echo', request_method='POST')
def echo_post(request):
    return request.json_body


@view_config(route_name='echo', request_method='PUT')
def echo_put(request):
    return request.json_body
