import requests
import transaction
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.exc import IntegrityError
from nthuion.views.base import View
from nthuion.auth.models import User, FacebookUser, Email
from nthuion.utils import keyerror_is_bad_request


class FacebookLogin(View):
    """
    Logging users in with facebook
    """

    @staticmethod
    def get_facebook_info(facebook_token):
        response = requests.get(
            'https://graph.facebook.com/v2.7/me',
            {
                'fields': 'id,name,email',
                'access_token': facebook_token
            }
        )
        if response.status_code == 400:
            raise HTTPBadRequest('Login failed: token rejected by facebook')
        json = response.json()
        return json['id'], json['name'], json.get('email')

    @staticmethod
    def fb_user_objects(facebook_id, name, email):
        user = User(name=name)
        if email is not None:
            email = Email(address=email, user=user, verified=True)
        fbusr = FacebookUser(user=user, id=facebook_id, name=name)
        return user, email, fbusr

    def post(self):
        """
        The body should look like this:

        .. code-block:: json

            {"token": "token_acquired_from_facebook"}

        the response will look like this:

        .. code-block:: json

            {"token": "2G5K7KBUeKpjSyz1PWmfV36hr83O0NoAIf7dqXz4DaDl"}

        Which is the token required for NTHU ION's API

        You should then put the token in the header for other requests,
        for example:

        .. sourcecode:: http

            GET /api/private/content HTTP/1.1
            Authorization: Token 2G5K7KBUeKpjSyz1PWmfV36hr83O0NoAIf7dqXz4DaDl

        :statuscode 200: on successful login
        :statuscode 400: - malformed POST body
                         - rejected facebook token
        """
        with keyerror_is_bad_request():
            facebook_token = self.request.json_body['token']
        fbid, name, email = self.get_facebook_info(facebook_token)
        user, emailobj, fbusr = self.fb_user_objects(fbid, name, email)
        self.request.db.add(user)
        if emailobj is not None:
            self.request.db.add(emailobj)
        self.request.db.add(fbusr)
        try:
            transaction.commit()
        except IntegrityError:
            transaction.abort()
        user = self.request.db.query(User)\
            .filter(FacebookUser.id == fbid)\
            .filter(User.id == FacebookUser.user_id)\
            .one()
        return {
            'token': user.acquire_token()
        }
