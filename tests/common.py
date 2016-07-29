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
