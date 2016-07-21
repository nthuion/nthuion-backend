from unittest import mock
from .base import BaseTest, WebTest


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


class FakeResponse:

    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def json(self):
        return self.data


def valid_user_response(*args, **kwargs):
    return FakeResponse(
        200,
        {
            'id': '34502913498532310',
            'name': '340gieoj3',
            'email': 'test@example.com'
        }
    )


def bad_request_response(*args, **kwargs):
    return FakeResponse(
        400,
        {
            'error': 'gg'
        }
    )


class FacebookLoginTest(WebTest):

    def test_facebook_login(self):
        with mock.patch('requests.get', valid_user_response):
            self.app.post_json(
                '/api/login/facebook',
                {'token': 'exxe'},
                status=200
            )
