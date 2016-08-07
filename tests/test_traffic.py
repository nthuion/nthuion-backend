from .base import WebTest
from nthuion.models import Issue, User
import transaction


class SmokeTest(WebTest):

    def test_set_up_class_is_working(self):
        self.ts.ping()

    def test_setup_1(self):
        assert 1 == self.ts.sadd('1', '2')

    def test_setup_2(self):
        """make sure that tearDown cleans the db correctly"""
        assert 1 == self.ts.sadd('1', '2')


class FakeObject:

    def __init__(self, id_):
        self.id = id_


class BasicTrafficTest(WebTest):

    def test_ts_ip(self):
        self.ts.article_viewed_by_ip(FakeObject(6), '127.0.0.1')

        assert 1 == self.ts.scard(6)
        assert b'ip:127.0.0.1' == self.ts.spop(6)

    def test_ts_user(self):
        self.ts.article_viewed_by_user(FakeObject(14), FakeObject(34))

        assert 1 == self.ts.scard(14)
        assert b'user:34' == self.ts.spop(14)

        self.ts.article_viewed_by_user(FakeObject(14), FakeObject(34))
        assert 1 == self.ts.scard(14)

        self.ts.article_viewed_by_user(FakeObject(14), FakeObject(932))
        assert 2 == self.ts.scard(14)

    def test_flush(self):
        with transaction.manager:
            user = User(name='test')
            self.session.add(user)
            issue = Issue(
                author=user,
                title='title',
                content='content',
                tags=[],
                is_anonymous=False,
            )
            self.session.add(issue)

        user = self.session.query(User).first()
        issue = self.session.query(Issue).first()

        self.ts.article_viewed_by_ip(issue, '127.0.0.1')
        self.ts.article_viewed_by_ip(issue, '192.168.1.1')
        self.ts.article_viewed_by_user(issue, user)
        self.ts.article_viewed_by_ip(issue, '192.168.1.1')

        self.ts.flush_traffic(self.session)

        assert 3 == self.session.query(Issue).first().views
        assert 3 == self.session.query(Issue).first().popularity

        self.ts.article_viewed_by_ip(issue, '127.0.0.1')
        self.ts.article_viewed_by_user(issue, user)
        self.ts.article_viewed_by_user(issue, user)

        self.ts.flush_traffic(self.session)

        assert 5 == self.session.query(Issue).first().views
        assert 5 == self.session.query(Issue).first().popularity
