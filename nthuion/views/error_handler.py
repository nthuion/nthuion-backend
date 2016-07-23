def error_view(exc, request):
    request.response.status = exc.code
    return {
        "error": exc.title,
        "code": exc.code,
        "detail": exc.detail
    }
