from nthuion.auth.views import FacebookLogin


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('echo', '/api/echo')

    config.add_route('facebook-login', '/api/login/facebook')
    config.add_view(FacebookLogin, route_name='facebook-login')
