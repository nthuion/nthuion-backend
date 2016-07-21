from .base import BaseTest


class AuthTest(BaseTest):

    def test_acquire_token(self):
        from nthuion.auth.models import User, Token
        self.assertEqual(0, self.session.query(Token).count())
        u = User(name='name')
        self.session.add(u)
        tvalue = u.acquire_token()
        self.assertEqual(1, self.session.query(Token).count())
        self.assertEqual(
            u,
            self.session.query(Token).filter(Token.value == tvalue).one().user
        )
