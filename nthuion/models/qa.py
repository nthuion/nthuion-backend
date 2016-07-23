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
from sqlalchemy.orm import relationship

import datetime

from .meta import Base
from .auth import User


class Entry(Base):

    id = Column(Integer, primary_key=True)

    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)

    poster_id = Column(Integer, ForeignKey(User.id), nullable=False)

    type = Column(String, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'entry',
        'polymorphic_on': type,
    }


class Article(Entry):

    id = Column(Integer, ForeignKey(Entry.id), primary_key=True)

    title = Column(String(80), nullable=False)

    content = Column(Text(30000), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'article'
    }


class Tag(Base):

    id = Column(Integer, primary_key=True)

    # note: stackoverflow uses 25
    name = Column(String(30), unique=True)


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


class Solution(Article):

    id = Column(Integer, ForeignKey(Article.id), primary_key=True)
    question_id = Column(Integer, ForeignKey(Question.id))


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
