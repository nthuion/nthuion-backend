import unittest
import transaction
from pyramid import testing
from webtest import TestApp as _TestApp

from nthuion import main
from nthuion.request import DummyRequest
from nthuion.models import get_engine, get_session_factory, get_tm_session
from nthuion.models.meta import Base


def dummy_request(dbsession):
    return DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('nthuion.models')
        settings = self.config.get_settings()

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.session = get_tm_session(session_factory, transaction.manager)

        Base.metadata.create_all(self.engine)

    def tearDown(self):
        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


class WebTest(unittest.TestCase):

    def setUp(self):
        app = main({}, **{
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        session_factory = app.registry['dbsession_factory']
        self.engine = session_factory.kw['bind']
        self.session = get_tm_session(session_factory, transaction.manager)
        Base.metadata.create_all(self.engine)

        self.app = _TestApp(app)
