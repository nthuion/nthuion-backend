from pyramid.view import view_config
from pyramid.httpexceptions import HTTPError


@view_config(context=HTTPError)
def notfound_view(exc, request):
    request.response.status = exc.code
    return {
        "error": exc.title,
        "code": exc.code,
    }
