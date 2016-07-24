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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, select
from sqlalchemy.ext import hybrid

import datetime

from .meta import Base
from .auth import User


class Entry(Base):

    id = Column(Integer, primary_key=True)

    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)

    author_id = Column(Integer, ForeignKey(User.id), nullable=False)
    author = relationship(User)

    type = Column(String, nullable=False)

    __mapper_args__ = {
        'polymorphic_on': type,
    }


class Article(Entry):

    id = Column(Integer, ForeignKey(Entry.id), primary_key=True)

    title = Column(String(80), nullable=False)

    content = Column(Text(30000), nullable=False)

    tags = relationship(
        'Tag',
        secondary=lambda: ArticleTag.__table__
    )

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


class Tag(Base):

    id = Column(Integer, primary_key=True)

    # note: stackoverflow uses 25
    name = Column(String(30), unique=True, index=True)

    @classmethod
    def get_or_create(cls, session, name):
        try:
            return session.query(cls).filter(cls.name == name).one()
        except NoResultFound:
            self = cls(name=name)
            session.add(self)
            return self

    @classmethod
    def from_names(cls, session, *names):
        return [cls.get_or_create(session, name) for name in names]

    def __repr__(self):
        return '<Tag {!r}>'.format(self.name)


class ArticleTag(Base):

    article_id = Column(Integer, ForeignKey(Article.id))
    tag_id = Column(Integer, ForeignKey(Tag.id))

    __table_args__ = (
        PrimaryKeyConstraint(article_id, tag_id),
    )


class Comment(Entry):

    id = Column(Integer, ForeignKey(Entry.id), primary_key=True)

    parent_id = Column(Integer, ForeignKey(Entry.id), nullable=False)
    parent = relationship(Entry, foreign_keys=parent_id)

    content = Column(Text(240), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'comment',
        'inherit_condition': Entry.id == id,
        # sesalso: http://stackoverflow.com/questions/14885042
    }


class Question(Article):

    id = Column(Integer, ForeignKey(Article.id), primary_key=True)
    is_anonymous = Column(Boolean, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'question'
    }

    def as_dict(self, viewer=None):
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
            'votes': self.votes
        }


class Solution(Article):

    id = Column(Integer, ForeignKey(Article.id), primary_key=True)
    question_id = Column(Integer, ForeignKey(Question.id))

    __mapper_args__ = {
        'polymorphic_identity': 'solution'
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
