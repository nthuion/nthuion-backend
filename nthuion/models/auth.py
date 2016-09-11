import random
import string

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref

from nthuion.models.meta import Base
from nthuion import roles


sysrand = random.SystemRandom()

alphanumeric = string.ascii_letters + string.digits


class User(Base):

    id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)

    __acl__ = [
        (roles.Allow, roles.Everyone, 'read'),
        (roles.Allow, roles.Owner, 'update')
    ]

    def acquire_token(self):
        tok = Token(self)
        self.object_session().add(tok)
        return tok.value

    def as_dict(self):
        fbusr = self.facebook_user
        if fbusr is None:
            avatar_url = None
        else:
            avatar_url = 'https://graph.facebook.com/%s/picture' % fbusr.id
        return {
            'id': self.id,
            'name': self.name,
            'avatar_url': avatar_url
        }

    def get_user_roles(self, user):
        if self.id == user.id:
            return [roles.Owner]
        else:
            return []

    def __repr__(self):
        return '<User {} {!r}>'.format(self.id, self.name)


class Token(Base):

    TOKEN_LENGTH = 255

    value = Column(String(TOKEN_LENGTH), primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey(User.id),
        index=True
    )
    user = relationship(User, backref='tokens')

    def __init__(self, user, value=None):
        if value is None:
            value = ''.join(
                sysrand.choice(alphanumeric)
                for i in range(self.TOKEN_LENGTH)
            )
        super().__init__(
            user=user,
            value=value
        )

    def __repr__(self):
        return '<Token {}... of user {}>'.format(self.value[:10], self.user.id)


class Email(Base):

    id = Column(Integer, primary_key=True)

    address = Column(String(254), nullable=False)
    # see also http://isemail.info/about

    user_id = Column(Integer, ForeignKey(User.id), index=True, nullable=False)
    user = relationship(User, backref='emails')

    verified = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<Email {!r}>'.format(self.address)


class FacebookUser(Base):

    id = Column(String(40), primary_key=True)
    # facebook says an id is a "numeric string"
    # https://developers.facebook.com/docs/graph-api/reference/v2.7/user

    name = Column(String(100), nullable=False)
    # facebook name of account
    # http://stackoverflow.com/questions/8078939

    user_id = Column(
        Integer,
        ForeignKey(User.id),
        unique=True,
        index=True,
        nullable=False
    )
    user = relationship(
        User,
        backref=backref('facebook_user', uselist=False)
    )

    def __repr__(self):
        return '<FacebookUser {} {!r}>'.format(self.id, self.name)
