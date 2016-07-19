import unittest
import transaction
from pyramid import testing

from .request import DummyRequest


def dummy_request(dbsession):
    return DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('.models')
        settings = self.config.get_settings()

        from .models import (
            get_engine,
            get_session_factory,
            get_tm_session,
        )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.session = get_tm_session(session_factory, transaction.manager)

        self.init_database()

    def init_database(self):
        from .models.meta import Base
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        from .models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


@unittest.skip('demo removed')
class TestMyViewSuccessCondition(BaseTest):

    def setUp(self):
        super(TestMyViewSuccessCondition, self).setUp()
        self.init_database()

        from .models import MyModel

        model = MyModel(name='one', value=55)
        self.session.add(model)

    def test_passing_view(self):
        from .views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'nthuion')


class AuthTest(BaseTest):

    def test_acquire_token(self):
        from nthuion.models import auth
        self.assertEqual(0, self.session.query(auth.Token).count())
        u = auth.User()
        self.session.add(u)
        u.acquire_token()
        self.assertEqual(1, self.session.query(auth.Token).count())


@unittest.skip('demo removed')
class TestMyViewFailureCondition(BaseTest):

    def test_failing_view(self):
        from .views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info.status_int, 500)


class WebTest(unittest.TestCase):

    def setUp(self):
        from . import main
        app = main({}, **{
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        from webtest import TestApp
        self.app = TestApp(app)


class TestEcho(WebTest):

    payload = {'nthu': 'ion', 'afg': 984}

    def test_get(self):
        res = self.app.get(
            '/api/echo',
            params=self.payload,
            status=200)

        # query string does not have
        self.assertEqual(
            {'nthu': ['ion'], 'afg': ['984']}, res.json)

    def test_post(self):
        res = self.app.post_json(
            '/api/echo',
            params=self.payload,
            status=200)
        self.assertEqual(self.payload, res.json)

    def test_invalid_request(self):
        self.app.post(
            '/api/echo',
            params=self.payload,
            status=400
        )
        self.app.put(
            '/api/echo',
            params=self.payload,
            status=400
        )

    def test_put(self):
        res = self.app.put_json(
            '/api/echo',
            params=self.payload,
            status=200
        )
        self.assertEqual(self.payload, res.json)


class IntrospectionTest(unittest.TestCase):

    def test_dry_run(self):
        import nthuion.introspect
        list(nthuion.introspect.r1())
