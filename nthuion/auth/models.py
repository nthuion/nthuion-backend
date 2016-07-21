import random
import string

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from nthuion.models.meta import Base


sysrand = random.SystemRandom()

alphanumeric = string.ascii_letters + string.digits


class User(Base):

    id = Column(Integer, primary_key=True)

    def acquire_token(self):
        tok = Token(self)
        self.object_session().add(tok)
        return tok.value

    def __repr__(self):
        return '<User id={}>'.format(self.id)


class Token(Base):

    TOKEN_LENGTH = 255

    value = Column(String(TOKEN_LENGTH), primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey(User.id),
        index=True
    )
    user = relationship(User, backref='tokens')

    def __init__(self, user):
        super().__init__(
            value=''.join(
                sysrand.choice(alphanumeric)
                for i in range(self.TOKEN_LENGTH)
            ),
            user=user
        )

    def __repr__(self):
        return '<Token {}... of {!r}>'.format(self.value[:10], self.user)


class Email(Base):

    id = Column(String(40), primary_key=True)

    email = Column(String(254), nullable=False)
    # see also http://isemail.info/about

    user_id = Column(Integer, ForeignKey(User.id), index=True, nullable=False)
    user = relationship(User, backref='emails')

    verified = Column(Boolean, default=False, nullable=False)


class FacebookUser(Base):

    id = Column(String(40), primary_key=True)
    # facebook says an id is a "numeric string"
    # https://developers.facebook.com/docs/graph-api/reference/v2.7/user

    access_token = Column(Text)

    user_id = Column(Integer, ForeignKey(User.id), unique=True, index=True)
    user = relationship(User, backref='facebook_user')
