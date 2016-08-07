import os
import subprocess
import threading
import transaction
import unittest
from pyramid import testing
from webtest import TestApp as _TestApp

from nthuion import main
from nthuion.request import DummyRequest
from nthuion.models import get_engine, get_session_factory, get_tm_session
from nthuion.models.meta import Base


def get_process_thread_identifier():
    return '{}-{}'.format(os.getpid(), threading.get_ident())


def dummy_request(dbsession):
    return DummyRequest(dbsession=dbsession)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:',
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

    @classmethod
    def setUpClass(cls):
        cls.redis_unixsocket = '/tmp/test-redis-{}.sock'.format(
            get_process_thread_identifier())
        cls.proc = subprocess.Popen(
            ['redis-server', '--wait']
        )

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait()

    def setUp(self):
        app = main({}, **{
            'sqlalchemy.url': 'sqlite:///:memory:',
            'redis.unixsocket': self.redis_unixsocket,
        })
        session_factory = app.registry['dbsession_factory']
        self.engine = session_factory.kw['bind']
        self.session = get_tm_session(session_factory, transaction.manager)
        Base.metadata.create_all(self.engine)

        self.app = _TestApp(app)
