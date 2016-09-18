import subprocess
from pyramid.httpexceptions import HTTPUnprocessableEntity, HTTPForbidden
import transaction
import itsdangerous
from sqlalchemy.orm.exc import NoResultFound

from nthuion.models import User, Email
from nthuion.utils import noresultfound_is_404
from nthuion.validation import body_schema, Required, Optional, All, Length
from .base import View, require_permission


class UserValidation:

    name = All(str, Length(max=User.name.type.length))


class UserView(View):
    """The user with the id"""

    @staticmethod
    def factory(request):
        id = request.matchdict['id']
        with noresultfound_is_404():
            return request.db.query(User).filter(User.id == id).one()

    def get(self):
        """returns the user object"""
        return self.context.as_dict()

    @require_permission('update')
    @body_schema({
        Optional('name'): UserValidation.name
    })
    def put(self, data):
        """update userdata, returns updated user object"""
        try:
            self.context.name = data['name']
        except KeyError:
            pass
        return self.context.as_dict()


class MeView(UserView):

    @staticmethod
    def factory(request):
        return request.authenticated_userid

    def get(self):
        """
        returns the currently logged in user object, with an additional
        attribute ``authenticated``

        if the user is not logged in, all attributes will be null
        """
        user = self.context
        if user is None:
            return {
                'id': None,
                'name': None,
                'avatar_url': None,
                'authenticated': False,
            }
        else:
            return {
                **user.as_dict(),
                'authenticated': True,
            }

    @require_permission('update')
    @body_schema({
        Optional('name'): UserValidation.name
    })
    def put(self, data):
        """update userdata, returns updated user object"""
        try:
            self.context.name = data['name']
        except KeyError:
            pass
        return self.context.as_dict()


def send_email(subject, to, content):
    return subprocess.run(
        ['mail', '-s', subject, to],
        input=content,
        universal_newlines=True,
        check=True
    )


class EmailView(View):

    @staticmethod
    def factory(request):
        if request.authenticated_userid is None:
            raise HTTPForbidden("You must log in")
        return request.authenticated_userid

    def get(self):
        """
        return the list of email objects

        .. code-block:: text

            {
                "data": [email objects...]
            }
        """
        user = self.context
        return {
            'data': [
                email.as_dict()
                for email
                in self.db.query(Email).filter(Email.user == user)
            ]
        }

    @body_schema({
        Required('address'): All(str, Length(min=3, max=254)),
    })
    def post(self, data):
        """
        requests the server to add a email to the current user
        """
        address = data['address']
        if not all(address.partition('@')):
            return HTTPUnprocessableEntity(
                '{!r} does not seem to be a valid email address'.format(
                    address
                )
            )
        token = self.request.signer.dumps(
            {'user_id': self.context.id, 'email': address})
        send_email(
            'Email verification',
            address,
            'verify your email at'
            'http://nthuion.cs.nthu.edu.tw/api/email/verify/{}'.format(token)
        )
        return {
            'message': 'verification email successfully sent'
        }


class EmailVerificationView:

    def get(self):
        token = self.request.matchdict['token']
        try:
            data = self.request.signer.loads(token, max_age=30 * 60)
        except itsdangerous.SignatureExpired:
            raise HTTPForbidden('The verification link expired')
        except itsdangerous.BadSignature:
            raise HTTPForbidden('Invalid verification token')

        try:
            user_id, email = data['user_id'], data['email']
        except KeyError:
            raise HTTPForbidden('Invalid verification token')

        try:
            user = self.db.query(User).filter(User.id == user_id).one()
        except:
            raise HTTPForbidden('Invalid verification token')

        try:
            user = self.session.query(User).filter(User.id == user_id).one()
        except NoResultFound:
            raise HTTPUnprocessableEntity('The user no longer exists')

        with transaction.manager:
            self.session.add(
                Email(address=email, verified=True, user=user))
        return {
            'message': 'successfully verified email: {}'.format(
                email
            )
        }
