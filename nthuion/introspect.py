import nthuion
from pprint import pprint as print


def r1():
    router = nthuion.main({}, **{'sqlalchemy.url': 'sqlite:///:memory:'})
    for view in router.registry.introspector.get_category('views'):
        intr = view['introspectable']
        name = intr['route_name']
        if name is None:
            continue
        yield name, router.routes_mapper.get_route(name), intr['callable']


print(list(r1()))
