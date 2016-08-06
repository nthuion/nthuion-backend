from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    SmallInteger,
    PrimaryKeyConstraint,
    CheckConstraint
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, select
from sqlalchemy.ext import hybrid

import datetime

from nthuion import roles

from .meta import Base
from .auth import User


class Entry(Base):

    id = Column(Integer, primary_key=True)

    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
    mtime = Column(DateTime, default=None)

    author_id = Column(Integer, ForeignKey(User.id), nullable=False)
    author = relationship(User)

    type = Column(String, nullable=False)

    __mapper_args__ = {
        'polymorphic_on': type,
    }

    def get_user_roles(self, user):
        if self.author_id == user.id:
            return [roles.Owner]
        else:
            return []

    def query_vote(self, user):
        """returns the query of current vote of the user.
        user must not be None"""
        return self.object_session().query(Vote)\
            .filter(Vote.entry_id == self.id)\
            .filter(Vote.user_id == user.id)

    def get_user_vote_value(self, user):
        """returns the vote of the user.
        returns -1, 0 or 1
        if user is None, returns 0
        """
        if user is None:
            return 0
        vote = self.query_vote(user).first()
        if vote is None:
            return 0
        else:
            return vote.value

    @hybrid.hybrid_property
    def votes(self):
        session = self.object_session()
        sum_ = session.query(func.sum(Vote.value))\
            .filter(Vote.entry_id == self.id).scalar()
        if sum_ is None:
            return 0
        return sum_

    @votes.expression
    def votes(cls):
        return select([func.sum(Vote.value)])\
            .where(Vote.entry_id == cls.id)\
            .label('votes')

    @hybrid.hybrid_property
    def ncomments(self):
        return self.object_session().query(Comment)\
            .filter(Comment.parent_id == self.id).count()

    @ncomments.expression
    def ncomments(cls):
        return select([func.count(Comment)])\
            .where(Comment.parent_id == cls.id)\
            .label('ncomments')


class Article(Entry):

    id = Column(Integer, ForeignKey(Entry.id), primary_key=True)

    title = Column(String(80), nullable=False)

    content = Column(Text(30000), nullable=False)

    tags = relationship(
        'Tag',
        secondary=lambda: ArticleTag.__table__
    )


class Tag(Base):

    id = Column(Integer, primary_key=True)

    # note: stackoverflow uses 25
    name = Column(String(30), unique=True, index=True)

    @classmethod
    def get_or_create(cls, session, name):
        assert len(name) <= cls.name.type.length
        res = session.query(cls).filter(cls.name == name).first()
        if res is not None:
            return res
        self = cls(name=name)
        session.add(self)
        try:
            session.flush()
        except IntegrityError:
            return session.query(cls).filter(cls.name == name).one()
        else:
            return self

    @classmethod
    def from_names(cls, session, names):
        assert isinstance(names, (list, tuple))
        session.flush()
        return [cls.get_or_create(session, name) for name in set(names)]

    def __repr__(self):
        return '<Tag {!r}>'.format(self.name)


class ArticleTag(Base):

    article_id = Column(Integer, ForeignKey(Article.id))
    tag_id = Column(Integer, ForeignKey(Tag.id))

    __table_args__ = (
        PrimaryKeyConstraint(article_id, tag_id),
    )


class Comment(Entry):

    __acl__ = [
        (roles.Allow, roles.Everyone, 'read'),
        (roles.Allow, roles.Owner, 'update'),
        (roles.Allow, roles.Authenticated, 'comment'),
        (roles.Allow, roles.Authenticated, 'vote'),
    ]

    id = Column(Integer, ForeignKey(Entry.id), primary_key=True)

    parent_id = Column(Integer, ForeignKey(Entry.id), nullable=False)
    parent = relationship(Entry, foreign_keys=parent_id)

    content = Column(Text(240), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'comment',
        'inherit_condition': Entry.id == id,
        # sesalso: http://stackoverflow.com/issues/14885042
    }

    def as_dict(self, user):
        return {
            'id': self.id,
            'parent': {
                'id': self.parent_id,
                'type': self.parent.type
            },
            'content': self.content,
            'author': self.author.as_dict(),
            'votes': self.votes,
            'ctime': self.ctime.isoformat(),
            'mtime': None if self.mtime is None else self.mtime.isoformat(),
            'user_vote': self.get_user_vote_value(user),
        }


class Issue(Article):

    __acl__ = [
        (roles.Allow, roles.Everyone, 'read'),
        (roles.Allow, roles.Authenticated, 'create'),
        (roles.Allow, roles.Owner, 'update'),
        (roles.Allow, roles.Authenticated, 'comment'),
        (roles.Allow, roles.Authenticated, 'vote'),
    ]

    id = Column(Integer, ForeignKey(Article.id), primary_key=True)
    is_anonymous = Column(Boolean, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'issue'
    }

    def as_dict(self, viewer):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': [tag.name for tag in self.tags],
            'author': (
                None
                if self.is_anonymous and viewer != self.author
                else self.author.as_dict()
            ),
            'is_anonymous': self.is_anonymous,
            'votes': self.votes,
            'ncomments': self.ncomments,
            'ctime': self.ctime.isoformat(),
            'mtime': None if self.mtime is None else self.mtime.isoformat(),
            'user_vote': self.get_user_vote_value(viewer),
        }


class Solution(Article):

    __acl__ = [
        (roles.Allow, roles.Everyone, 'read'),
        (roles.Allow, roles.Authenticated, 'create'),
        (roles.Allow, roles.Owner, 'update'),
        (roles.Allow, roles.Authenticated, 'comment'),
        (roles.Allow, roles.Authenticated, 'vote'),
    ]

    id = Column(Integer, ForeignKey(Article.id), primary_key=True)
    issue_id = Column(Integer, ForeignKey(Issue.id))
    issue = relationship(
        Issue,
        foreign_keys=issue_id,
        backref='solutions')

    __mapper_args__ = {
        'polymorphic_identity': 'solution'
    }

    def as_dict(self, user):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': [tag.name for tag in self.tags],
            'author': self.author.as_dict(),
            'issue': {
                'id': self.issue.id,
                'title': self.issue.title
            } if self.issue is not None else None,
            'votes': self.votes,
            'ncomments': self.ncomments,
            'ctime': self.ctime.isoformat(),
            'mtime': None if self.mtime is None else self.mtime.isoformat(),
            'user_vote': self.get_user_vote_value(user),
        }


class Vote(Base):

    user_id = Column(Integer, ForeignKey(User.id))
    entry_id = Column(Integer, ForeignKey(Entry.id), index=True)

    value = Column(
        SmallInteger,
        CheckConstraint('value == 1 OR value == -1', name='vote_is_one'),
    )

    __table_args__ = (
        PrimaryKeyConstraint(user_id, entry_id),
    )
