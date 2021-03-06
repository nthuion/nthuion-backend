from zope.interface import implementer
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized
from sqlalchemy.orm.exc import NoResultFound
from .models import User, Token
from .roles import Authenticated, Everyone, Nthu


@implementer(IAuthenticationPolicy)
class TokenAuthenticationPolicy:

    def forget(self, request):
        value = self.unauthenticated_userid(request)
        if value is not None:
            request.db.query(Token.value == value).delete()

    def remember(self, request, userid, **kw):
        pass
        # the login functions does it well

    def authenticated_userid(self, request):
        value = self.unauthenticated_userid(request)
        if value is None:
            return None
        try:
            return request.db.query(User)\
                .filter(Token.value == value)\
                .filter(Token.user_id == User.id)\
                .one()
        except NoResultFound:
            raise HTTPUnauthorized('Invalid token')

    def unauthenticated_userid(self, request):
        authorization = request.headers.get('Authorization')
        if authorization is not None:
            try:
                type_, value = authorization.split(maxsplit=1)
                if type_ != 'Token':
                    raise HTTPBadRequest(
                        'Unknown Authorization type {}'.format(type_)
                    )
                else:
                    return value
            except ValueError:
                raise HTTPBadRequest('Invalid Authorization header format')
        else:
            return None

    def effective_principals(self, request):
        user = self.authenticated_userid(request)
        if user is None:
            return [Everyone]
        else:
            principals = [Everyone, Authenticated]
            if user.is_nthu_verified():
                principals.append(Nthu)
            ctx = request.context
            if not isinstance(ctx, type) and hasattr(ctx, 'get_user_roles'):
                return ctx.get_user_roles(user) + [Everyone, Authenticated]
            return principals
