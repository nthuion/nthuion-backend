from pyramid.httpexceptions import HTTPError
from nthuion.views import echo, auth, error_handler, questions


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_view(error_handler.error_view, context=HTTPError)

    def add(path, view, name):
        config.add_route(
            name,
            path,
            factory=getattr(view, 'factory', None),
        )
        config.add_view(
            view,
            route_name=name,
        )

    add('/api/echo', echo.EchoView, 'echo')
    add('/api/login/facebook', auth.FacebookLogin, 'facebook-login')
    add('/api/logout', auth.Logout, 'logout')
    add('/api/questions', questions.QuestionList, 'questions')
    add('/api/questions/{id}', questions.QuestionView, 'question')
