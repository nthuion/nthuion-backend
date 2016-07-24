def error_view(exc, request):
    request.response.status = exc.code
    return {
        'error': {
            'title': exc.title,
            'code': exc.code,
            'message': exc.detail
        }
    }
