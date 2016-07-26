import transaction
from .base import WebTest
from nthuion.models import User, FacebookUser


class UserTest(WebTest):
    def prepare(self):
        with transaction.manager:
            self.session.add(User(name='test'))

    def prepare_fb(self):
        with transaction.manager:
            u = User(name='test')
            self.session.add(u)
            self.session.add(
                FacebookUser(id='LoremFacebookIpsum', user=u, name='fbu')
            )

    def test_me_anony(self):
        self.prepare()
        res = self.app.get(
            '/api/users/me'
        )
        self.assertEqual(
            {
                'authenticated': False,
                'name': None,
                'id': None,
                'avatar_url': None
            },
            res.json
        )

    def test_me_logged_in(self):
        self.prepare()
        with transaction.manager:
            token = self.session.query(User).first().acquire_token()
        user = self.session.query(User).first()
        res = self.app.get(
            '/api/users/me',
            headers={
                'Authorization': 'Token {}'.format(token)
            }
        )
        self.assertEqual(True, res.json['authenticated'])
        self.assertEqual(user.name, res.json['name'])
        self.assertEqual(user.id, res.json['id'])
        self.assertEqual(None, res.json['avatar_url'])

    def test_facebook_logged_in(self):
        self.prepare_fb()
        with transaction.manager:
            token = self.session.query(User).first().acquire_token()
        user = self.session.query(User).first()
        res = self.app.get(
            '/api/users/me',
            headers={
                'Authorization': 'Token {}'.format(token)
            }
        )
        self.assertEqual(True, res.json['authenticated'])
        self.assertEqual(user.name, res.json['name'])
        self.assertEqual(user.id, res.json['id'])
        self.assertEqual(
            'https://graph.facebook.com/LoremFacebookIpsum/picture',
            res.json['avatar_url']
        )

    def test_user_one(self):
        self.prepare()
        user = self.session.query(User).first()
        expected = user.as_dict()
        res = self.app.get(
            '/api/users/{}'.format(user.id),
        )
        self.assertEqual(expected, res.json)

    def test_user_404(self):
        self.app.get(
            '/api/users/404',
            status=404
        )
