from unittest.mock import patch
import transaction
from .base import WebTest

from nthuion.models import User, Email


@patch('nthuion.views.users.send_email', autospec=True)
class EmailVerificationMailTest(WebTest):
    def setUp(self):
        super().setUp()
        with transaction.manager:
            user = User(name='afg')
            self.session.add(user)
            self.token = self.session.query(User).one().acquire_token()

    def add_email(self, email, **kwargs):
        self.app.post_json(
            '/api/users/me/emails',
            {'address': email},
            headers={'Authorization': 'Token {}'.format(self.token)},
            **kwargs
        )

    def test_email_sent_when_POST_to_email_add(self, send_email):
        self.add_email('afg@example.com')
        assert 1 == send_email.call_count
        subject, to, content = send_email.call_args[0]
        assert 'afg@example.com' == to

    def add_email_and_verify(self, email, send_email):
        self.add_email(email)
        subject, to, content = send_email.call_args[0]
        self.app.get(
            content.split('http://nthuion.cs.nthu.edu.tw')[-1].split()[0]
        )

    def test_verify_email(self, send_email):
        self.add_email_and_verify('afg@example.com', send_email)
        email = self.session.query(Email).one()
        assert email.user.name == 'afg'
        assert email.address == 'afg@example.com'
        assert email.verified
        assert not self.session.query(User).one().is_nthu_verified()

        data = self.app.get(
            '/api/users/me/emails',
            headers={'Authorization': 'Token {}'.format(self.token)},
        ).json_body
        assert {'data': [email.as_dict()]} == data

    def test_nthu_verified(self, send_email):
        self.add_email_and_verify('afg@example.com', send_email)
        assert not self.session.query(User).one().is_nthu_verified()
        self.add_email_and_verify('afg@nthu.edu.tw', send_email)
        assert self.session.query(User).one().is_nthu_verified()
        self.add_email_and_verify('some@other.email', send_email)
        assert self.session.query(User).one().is_nthu_verified()

    def test_invalid_email(self, send_email):
        self.add_email('thisIsNotAValidAddress', status=422)

    def test_email_added_already(self, send_email):
        self.add_email_and_verify('afg@example.com', send_email)
        self.add_email_and_verify('afg@example.com', send_email)
        assert 1 == self.session.query(Email).count()
