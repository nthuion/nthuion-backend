import transaction
from .base import WebTest, BaseTest
from nthuion.models import User, FacebookUser, Email


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

    def test_user_put_me_no_edit(self):
        self.prepare_fb()
        with transaction.manager:
            token = self.session.query(User).first().acquire_token()
        user = self.session.query(User).first()
        res = self.app.put_json(
            '/api/users/me',
            {},
            headers={
                'Authorization': 'Token {}'.format(token)
            }
        )
        self.assertEqual(user.name, res.json['name'])
        self.assertEqual(user.id, res.json['id'])
        self.assertEqual(
            'https://graph.facebook.com/LoremFacebookIpsum/picture',
            res.json['avatar_url']
        )

    def test_user_put_id_no_edit(self):
        self.prepare_fb()
        with transaction.manager:
            token = self.session.query(User).first().acquire_token()
        user = self.session.query(User).first()
        res = self.app.put_json(
            '/api/users/{}'.format(self.session.query(User).first().id),
            {},
            headers={
                'Authorization': 'Token {}'.format(token)
            }
        )
        self.assertEqual(user.name, res.json['name'])
        self.assertEqual(user.id, res.json['id'])
        self.assertEqual(
            'https://graph.facebook.com/LoremFacebookIpsum/picture',
            res.json['avatar_url']
        )

    def test_user_put_me_update_username(self):
        self.prepare_fb()
        with transaction.manager:
            token = self.session.query(User).first().acquire_token()
        id_ = self.session.query(User).first().id
        res = self.app.put_json(
            '/api/users/me',
            {'name': 'zzoozzoz'},
            headers={
                'Authorization': 'Token {}'.format(token)
            }
        )
        self.assertEqual('zzoozzoz', res.json['name'])
        self.assertEqual(id_, res.json['id'])
        self.assertEqual(
            'https://graph.facebook.com/LoremFacebookIpsum/picture',
            res.json['avatar_url']
        )
        self.assertEqual('zzoozzoz', self.session.query(User).first().name)

    def test_user_put_id_update_username(self):
        self.prepare_fb()
        with transaction.manager:
            token = self.session.query(User).first().acquire_token()
        id_ = self.session.query(User).first().id
        res = self.app.put_json(
            '/api/users/{}'.format(self.session.query(User).first().id),
            {'name': 'qaqaqaq'},
            headers={
                'Authorization': 'Token {}'.format(token)
            }
        )
        self.assertEqual('qaqaqaq', res.json['name'])
        self.assertEqual(id_, res.json['id'])
        self.assertEqual(
            'https://graph.facebook.com/LoremFacebookIpsum/picture',
            res.json['avatar_url']
        )
        self.assertEqual('qaqaqaq', self.session.query(User).first().name)


class EmailVerificationTest(BaseTest):

    def setUp(self):
        super().setUp()

        user = User(name='afg')
        with transaction.manager:
            self.session.add(user)

    def get_user(self):
        return self.session.query(User).one()

    def add_email(self, address, verified):
        with transaction.manager:
            self.session.add(
                Email(user=self.get_user(), address=address, verified=verified)
            )

    def test_has_not_verified_not_nthu_email(self):
        self.add_email('afg@nthuion.backend', False)
        self.assertFalse(self.get_user().is_nthu_verified())

    def test_has_verified_not_nthu_email(self):
        self.add_email('afg@nthuion.backend', True)
        self.assertFalse(self.get_user().is_nthu_verified())

    def test_has_many_not_nthu_email(self):
        self.add_email('afg@nthuion.backend', True)
        self.add_email('afg@nthuion.frontend', True)
        self.add_email('afg@nthu.fake.edu.tw', True)
        self.add_email('nthu.edu.tw@gmail.com', True)
        self.assertFalse(self.get_user().is_nthu_verified())

    def test_has_not_verified_nthu_email(self):
        self.add_email('afg@nthu.edu.tw', False)
        self.assertFalse(self.get_user().is_nthu_verified())

    def test_has_verified_nthu_email(self):
        self.add_email('afg@nthu.edu.tw', True)
        self.assertTrue(self.get_user().is_nthu_verified())

    def test_has_one_verified_nthu_email(self):
        self.add_email('afg@nthu.edu.tww', True)
        self.add_email('afg2@nthu.edu.tw', False)
        self.add_email('afg@nthu.edu.tw', True)
        self.add_email('afg@nthu.edu.twz', True)
        self.assertTrue(self.get_user().is_nthu_verified())
