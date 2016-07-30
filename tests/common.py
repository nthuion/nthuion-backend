import transaction
from .base import WebTest
from nthuion.models import User


class OneUserTest(WebTest):

    def setUp(self):
        super().setUp()
        with transaction.manager:
            user = User(name='lorem')
            self.session.add(user)
            self.token = user.acquire_token()
            self.token_header = {
                'Authorization': 'Token {}'.format(self.token)
            }
        self.uid, = self.session.query(User.id).first()


class ManyUserTest(WebTest):

    def setUp(self):
        super().setUp()
        with transaction.manager:
            u1 = User(name='username1')
            u2 = User(name='username2')
            u3 = User(name='username3')
            self.session.add(u1)
            self.session.add(u2)
            self.session.add(u3)
            self.tok1 = u1.acquire_token()
            self.tok2 = u2.acquire_token()
            self.tok3 = u3.acquire_token()
        (self.u1,), (self.u2,), (self.u3,) = \
            self.session.query(User.id).order_by(User.name)

    @staticmethod
    def make_token_header(token):
        return {'Authorization': 'Token {}'.format(token)}
