import transaction
from .base import WebTest
from nthuion.models import User


class UserTest(WebTest):
    def prepare(self):
        with transaction.manager:
            self.session.add(User(name='test'))

    def test_me_anony(self):
        self.prepare()
        res = self.app.get(
            '/api/users/me'
        )
        self.assertEqual(
            {
                'authenticated': False,
                'name': None,
                'id': None
            },
            res.json
        )

    def test_me_logged_in(self):
        self.prepare()
        with transaction.manager:
            user = self.session.query(User).first()
            token = user.acquire_token()
        user = self.session.query(User).first()
        res = self.app.get(
            '/api/users/me',
            headers={
                'Authorization': 'Token {}'.format(token)
            }
        )
        self.assertEqual(
            {
                'authenticated': True,
                'name': user.name,
                'id': user.id
            },
            res.json
        )

    def test_user_one(self):
        self.prepare()
        user = self.session.query(User).first()
        res = self.app.get(
            '/api/users/{}'.format(user.id),
        )
        self.assertEqual(user.as_dict(), res.json)

    def test_user_404(self):
        self.app.get(
            '/api/users/404',
            status=404
        )
