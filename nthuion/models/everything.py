from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    PrimaryKeyConstraint
)

import datetime

from .meta import Base


class User(Base):

    id = Column(Integer, primary_key=True)


class Tag(Base):

    id = Column(Integer, primary_key=True)

    # note: stackoverflow uses 25
    name = Column(String(30))


class Likable(Base):

    id = Column(Integer, primary_key=True)


class Article(Base):

    id = Column(Integer, primary_key=True)

    title = Column(String(80), nullable=False)

    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)

    poster_id = Column(Integer, nullable=False)

    content = Column(Text(30000), nullable=False)


class Question(Article):

    id = Column(Integer, ForeignKey(Article.id), primary_key=True)
    is_anonymous = Column(Boolean, nullable=False)


class QuestionTag(Base):

    question_id = Column(Integer, ForeignKey(Question.id))
    tag_id = Column(Integer, ForeignKey(Tag.id))

    __table_args__ = (
        PrimaryKeyConstraint('question_id', 'tag_id'),
    )


class Solution(Article):

    id = Column(Integer, ForeignKey(Article.id), primary_key=True)
    question_id = Column(Integer, ForeignKey(Question.id))


class SolutionTag(Base):

    solution_id = Column(Integer, ForeignKey(Solution.id))
    tag_id = Column(Integer, ForeignKey(Tag.id))

    __table_args__ = (
        PrimaryKeyConstraint('solution_id', 'tag_id'),
    )


class Comment(Base):

    id = Column(Integer, primary_key=True)

    article_id = Column(Integer, ForeignKey(Article.id))
    parent_id = Column(Integer, ForeignKey('comment.id'))

    poster_id = Column(Integer)
