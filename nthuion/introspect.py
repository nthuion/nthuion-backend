import nthuion
from nthuion.views.base import View


def r1():
    router = nthuion.main({}, **{'sqlalchemy.url': 'sqlite:///:memory:'})
    for view in router.registry.introspector.get_category('views'):
        intr = view['introspectable']
        name = intr['route_name']
        if name is None:
            continue
        vcallable = intr['callable']
        if isinstance(vcallable, type) and issubclass(vcallable, View):
            yield name, router.routes_mapper.get_route(name).path, vcallable
