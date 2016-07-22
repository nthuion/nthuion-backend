from nthuion.auth.views import FacebookLogin, Logout
from nthuion.views.questions import QuestionList


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('echo', '/api/echo')

    config.add_route('facebook-login', '/api/login/facebook')
    config.add_view(FacebookLogin, route_name='facebook-login')

    config.add_route('logout', '/api/logout')
    config.add_view(Logout, route_name='logout')

    config.add_route('questions', '/api/questions')
    config.add_view(QuestionList, route_name='questions')
